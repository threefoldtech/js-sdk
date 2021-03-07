import gevent
import pytest
from jumpscale.loader import j
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase


@pytest.mark.integration
class VDCDashboard(VDCBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wallet = cls._import_wallet("demos_wallet")

    def tearDown(self):
        self.vdc.provision_wallet.merge_into_account(self.wallet.address)
        self.vdc.prepaid_wallet.merge_into_account(self.wallet.address)
        j.sals.vdc.delete(self.vdc.instance_name)

        super().tearDown()

    def test01_vdc_backup(self):
        """Test case for backup and restore a VDC.

        **Test Scenario**

        - Deploy VDC.
        - Deploy a cryptpad.
        - Backup a VDC.
        - Delete this VDC.
        - Redeploy VDC with same name and password.
        - Restore backup.
        - Check that cryptpad reachable.
        """

        self.info("Deploy VDC")
        self.vdc_name = self.random_name().lower()
        self.password = self.random_string()
        kube_config = self.deploy_vdc(self.vdc_name, self.password)

        self.info("Deploy a cryptpad")
        name = self.random_name().lower()
        cryptpad = deployer.deploy_cryptpad(release_name=name)

        self.info("Backup a VDC")
        j.sals.fs.copy_file(
            f"{j.sals.fs.home()}/sandbox/cfg/vdc/kube/{self.vdc.owner_tname}/{self.vdc.vdc_name}.yaml",
            j.sals.fs.expanduser("~/.kube/config"),
        )
        backup_name = self.random_name().lower()
        self.create_backup(backup_name)

        self.info("Delete this VDC")
        self.vdc.provision_wallet.merge_into_account(self.wallet.address)
        self.vdc.prepaid_wallet.merge_into_account(self.wallet.address)
        j.sals.vdc.delete(self.vdc.instance_name)

        self.info("Redeploy VDC with same name and password")
        kube_config = self.deploy_vdc(self.vdc_name, self.password)

        self.info("Restore backup")
        self.restore_backup(backup_name=backup_name)

        self.info("Check that cryptpad has been reachable")
        request = j.tools.http.get(url=f"https://{cryptpad.domain}", timeout=180, verify=False)
        self.assertEqual(request.status_code, 200)

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
