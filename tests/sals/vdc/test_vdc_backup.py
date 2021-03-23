import gevent
import pytest
from jumpscale.clients.explorer.models import K8s
from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase
from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase
from parameterized import parameterized_class
from jumpscale.clients.stellar import TRANSACTION_FEES


@parameterized_class(("no_deployment"), [("single",)])
@pytest.mark.integration
class VDCDashboard(VDCBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._import_wallet("demos_wallet")
        cls.flavor = "silver"

        cls.vdc_name = cls.random_name().lower()
        cls.password = cls.random_string()
        cls.kube_config = cls.deploy_vdc(cls.vdc_name, cls.password)

        if not cls.kube_config:
            raise RuntimeError("VDC is not deployed")

        j.sals.fs.copy_file(
            f"{j.sals.fs.home()}/sandbox/cfg/vdc/kube/{cls.vdc.owner_tname}/{cls.vdc.vdc_name}.yaml",
            j.sals.fs.expanduser("~/.kube/config"),
        )
        cls.kube_manager = j.sals.kubernetes.Manager()

        cls.info("Check that resources are available and ready in 5 min maximum")
        cls.kube_monitor = cls.vdc.get_kubernetes_monitor()
        has_resource = False
        resources_expiry = j.data.time.now().timestamp + 300
        while j.data.time.now().timestamp < resources_expiry and not has_resource:
            res = cls.kube_monitor.fetch_resource_reservations()
            for node in res:
                if node.has_enough_resources(1000, 1024):
                    cls.info("Cluster resources are ready")
                    has_resource = True
                    break

        cls.timeout = 60
        # Accept Marketplace T&C for testing identity.
        ChatflowsBase.tname = cls.tname
        ChatflowsBase.accept_terms_conditions(type_="marketplace")

    @classmethod
    def tearDownClass(cls):
        wallet = j.clients.stellar.get("demos_wallet")
        cls.vdc.provision_wallet.merge_into_account(wallet.address)
        cls.vdc.prepaid_wallet.merge_into_account(wallet.address)
        j.sals.vdc.delete(cls.vdc.instance_name)
        super().tearDownClass()

    def _get_and_wait_ssl(self, domain, expire_timeout=180):
        expiry = j.data.time.now().timestamp + expire_timeout
        is_certified = False
        request = None
        while j.data.time.now().timestamp < expiry:
            try:
                request = j.tools.http.get(domain, timeout=self.timeout)
                is_certified = True
                break
            except j.tools.http.exceptions.SSLError:
                self.info("Waiting to check ssl certificate....")
                gevent.sleep(10)

        if not is_certified:
            j.logger.warning(
                f"{domain} can't gain a ssl certificate, it maybe take longer than {expire_timeout/60} min to resolve it, check again later!"
            )
            request = j.tools.http.get(domain, timeout=self.timeout, verify=False)

        return request

    def create_backup(self, backup_name):
        config_path = j.sals.fs.expanduser("~/.kube/config")
        client = j.sals.kubernetes.Manager(config_path=config_path)

        try:
            client.execute_native_cmd(
                f"velero create backup config-{backup_name} --include-resources secrets,configmaps"
            )
            client.execute_native_cmd(f'velero create backup vdc-{backup_name} -l "backupType=vdc"')
        except Exception as e:
            raise RuntimeError(f"Failed to create backup due to {str(e)}")

    def restore_backup(self, backup_name):
        config_path = j.sals.fs.expanduser("~/.kube/config")
        client = j.sals.kubernetes.Manager(config_path=config_path)

        try:
            client.execute_native_cmd(
                f"velero create restore restore-vdc-{backup_name} --from-backup vdc-{backup_name}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to restore backup due to {str(e)}")

    def test01_vdc_backup(self):
        """Test case for backup and restore a VDC.

        **Test Scenario**

        - Deploy VDC.
        - Deploy a cryptpad.
        - Check that cryptpad has been reachable.
        - Backup a VDC.
        - Delete this cryptpad.
        - Restore backup.
        - Check that cryptpad reachable.
        """
        self.info("Deploy a Cryptpad.")
        name = self.random_name().lower()
        cryptpad = deployer.deploy_cryptpad(release_name=name)
        cryptpad_domain = cryptpad.domain

        self.info("Check that cryptpad has been reachable")
        request = j.tools.http.get(url=f"https://{cryptpad.domain}", timeout=180, verify=False)
        self.assertEqual(request.status_code, 200)

        self.info("Backup a VDC")
        backup_name = self.random_name().lower()
        self.create_backup(backup_name)

        self.info("Delete this cryptpad")
        kube_manager = j.sals.kubernetes.Manager()
        kube_manager.execute_native_cmd(f"kubectl delete ns {cryptpad.chart_name}-{cryptpad.release_name}")

        self.info("Restore backup")
        self.restore_backup(backup_name)

        self.info("Check that cryptpad has been reachable")
        request = j.tools.http.get(url=f"https://{cryptpad_domain}", timeout=600, verify=False)
        self.assertEqual(request.status_code, 200)
