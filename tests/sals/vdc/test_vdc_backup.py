import os

from gevent import sleep
import pytest
from jumpscale.clients.explorer.models import K8s
from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase
from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase
from parameterized import parameterized_class
from jumpscale.clients.stellar import TRANSACTION_FEES
from solutions_automation.vdc import deployer


@pytest.mark.integration
class VDCDashboard(VDCBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._import_wallet(wallet_name="vdc_init")
        cls._import_wallet(wallet_name="grace_period")
        cls.config_vdc = j.core.config.get("VDC_INITIALIZATION_WALLET")
        j.core.config.set("VDC_INITIALIZATION_WALLET", "vdc_init")

        backup_vars = ["S3_URL", "S3_BUCKET", "S3_AK", "S3_SK"]
        for var in backup_vars:
            value = os.environ.get(var)
            if not value:
                raise ValueError(f"Please add {var} as environment variables")
            setattr(cls, var, value)
        s3_local_config = {"S3_URL": cls.S3_URL, "S3_BUCKET": cls.S3_BUCKET, "S3_AK": cls.S3_AK, "S3_SK": cls.S3_SK}
        j.config.set("VDC_S3_CONFIG", s3_local_config)

    @classmethod
    def tearDownClass(cls):
        if cls.config_vdc:
            j.core.config.set("VDC_INITIALIZATION_WALLET", cls.config_vdc)
        j.config.set("VDC_S3_CONFIG", {})
        super().tearDownClass()

    def tearDown(self):
        self.info("Delete a VDC")
        if self.vdc:
            vdc = self.vdc.vdc
        else:
            vdc = j.sals.vdc.get(f"vdc_{self.vdc_name}_{self.tname}")

        j.sals.vdc.delete(vdc.instance_name)
        wallet = j.clients.stellar.get("demos_wallet")
        vdc.provision_wallet.merge_into_account(wallet.address)
        vdc.prepaid_wallet.merge_into_account(wallet.address)

        super().tearDown()

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

        - Prepare ssh key
        - Deploy VDC.
        - Deploy a cryptpad.
        - Check that cryptpad has been reachable.
        - Up wireguard
        - Backup a VDC.
        - Delete this cryptpad.
        - Restore backup.
        - Check that cryptpad reachable.
        """

        self.info("Prepare ssh key")
        self.ssh_client_name = self.random_name()
        if not j.sals.fs.exists("/tmp/.ssh"):
            j.core.executors.run_local('mkdir /tmp/.ssh && ssh-keygen -t rsa -f /tmp/.ssh/id_rsa -q -N "" ')
        self.ssh_cl = j.clients.sshkey.get(self.ssh_client_name)
        self.ssh_cl.private_key_path = "/tmp/.ssh/id_rsa"
        self.ssh_cl.load_from_file_system()
        self.ssh_cl.save()

        self.info("Deploy a VDC")
        self.vdc_name = self.random_name().lower()
        password = self.random_string()
        flavor = "silver"
        self.vdc = deployer.deploy_vdc(self.vdc_name, password, flavor.upper())

        self.info("Deploy a Cryptpad.")
        name = self.random_name().lower()
        cryptpad = deployer.deploy_cryptpad(release_name=name)
        cryptpad_domain = cryptpad.domain

        self.info("Check that cryptpad has been reachable")
        request = j.tools.http.get(url=f"https://{cryptpad.domain}", timeout=180, verify=False)
        self.assertEqual(request.status_code, 200)

        self.info("Up wireguard")
        threebot = self.vdc.vdc.threebot
        self.wg_conf_paths.append(f"/tmp/{self.random_name()}.conf")
        j.sals.fs.write_file(self.wg_conf_paths[-1], threebot.wgcfg)
        rc, out, err = j.sals.process.execute(f"sudo wg-quick up {self.wg_conf_paths[-1]}")
        sleep(5)

        self.info("Backup a VDC")
        localclient = j.clients.sshclient.get(self.ssh_client_name)
        localclient.sshkey = self.ssh_client_name
        localclient.host = threebot.ip_address
        localclient.save()

        backup_name = self.random_name().lower()
        _, res, _ = localclient.sshclient.run(
            f"velero create backup config-{backup_name} --include-resources secrets,configmaps"
        )
        _, res, _ = localclient.sshclient.run(f'velero create backup vdc-{backup_name} -l "backupType=vdc"')

        self.info("Delete this cryptpad")
        # how delete cryptpad

        self.info("Restore backup")
        _, res, _ = localclient.sshclient.run(
            f"velero create restore restore-vdc-{backup_name} --from-backup vdc-{backup_name}"
        )

        self.info("Check that cryptpad has been reachable")
        request = j.tools.http.get(url=f"https://{cryptpad_domain}", timeout=600, verify=False)
        self.assertEqual(request.status_code, 200)
