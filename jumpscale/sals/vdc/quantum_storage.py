import os
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import _get_zstor_config


ZDB_HOOK_URL = "https://raw.githubusercontent.com/threefoldtech/quantum-storage/master/lib/zdb-hook.sh"
ZDB_HOOK_PATH = "/home/rancher/0-db-fs/zdb_hook.sh"
ZSTORCONF_PATH = "/etc/zstor-default.toml"


class QuantumStorage:
    def __init__(self, vdc, ip_version=4):
        self.zstor_config = None
        self.vdc = vdc
        self.ip_version = ip_version  # to use in zstor config

    def update_zstor_config(self, endpoints, prefix="someprefix", etcd_secret=None):
        config = _get_zstor_config(self.ip_version)
        config["meta"]["config"]["endpoints"] = endpoints
        config["meta"]["config"]["prefix"] = prefix
        config["meta"]["config"]["username"] = "root"
        config["meta"]["config"]["password"] = etcd_secret
        return j.data.serializers.toml.dumps(config)

    def apply(self, mount_location="/home/rancher/mounted"):
        for kubernetes_node in self.vdc.kubernetes:
            j.logger.info(f"Initalizing quantum storage on node: {kubernetes_node.wid}")
            ssh_client = self.vdc.get_ssh_client(
                f"qs_init_{kubernetes_node.wid}", kubernetes_node.ip_address, "rancher"
            )
            j.logger.info(f"Downloading zdb hook on: {kubernetes_node.wid} in {ZDB_HOOK_PATH}")

            zdb_hook_data = None
            try:
                zdb_hook_res = j.tools.http.get(ZDB_HOOK_URL)
                zdb_hook_res.raise_for_status()
                zdb_hook_data = zdb_hook_res.text
                j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/zdb_hook.sh", zdb_hook_data)
            except Exception as e:
                j.logger.critical(
                    f"Failed to download zdb hook on: {kubernetes_node.wid} due to {str(e)}, It will be used from cache."
                )
                if not j.sals.fs.exists(f"{j.core.dirs.CFGDIR}/vdc/zdb_hook.sh"):
                    raise e
                zdb_hook_data = j.sals.fs.read_file(f"{j.core.dirs.CFGDIR}/vdc/zdb_hook.sh")

            ssh_client.sshclient.run(
                f"mkdir -p /home/rancher/0-db-fs/ && echo '''{zdb_hook_data}''' > {ZDB_HOOK_PATH} && chmod +x {ZDB_HOOK_PATH}"
            )

            j.logger.info(f"Creating dirs on: {kubernetes_node.wid} ...")
            ssh_client.sshclient.run(f"sudo mkdir -p /zdb/data /zdb/index && sudo chown -R rancher:rancher /zdb")

            try:
                ssh_client.sshclient.run(
                    f"sudo mkdir -p {mount_location} && sudo chown -R rancher:rancher {mount_location} && sudo chmod 777 {mount_location}"
                )
            except Exception as e:
                j.logger.warning(f"failed to create directory {mount_location}, exists already")
            j.logger.info(f"Updating fuse config file on: {kubernetes_node.wid}")
            ssh_client.sshclient.run("sudo sed -i /#user_allow_other/c\\user_allow_other /etc/fuse.conf")

            j.logger.info(f"Downloading zdbstor config on: {kubernetes_node.wid} in {ZSTORCONF_PATH}")

            deployments = get_deployments(solution_type="etcd", username=self.vdc.owner_tname)
            etcd_secret = self.vdc.get_password()
            for deployment in deployments:
                if "etcdqs" in deployment.get("Release"):
                    domain = deployment.get("Domain")
                    etcd_domain = f"https://{domain}:2379"
                    break
            else:
                from solutions_automation.vdc.deployer import deploy_etcd

                domain = deploy_etcd(
                    f"etcdqs-{kubernetes_node.wid}",
                    sub_domain="Choose a custom subdomain on a gateway",
                    custom_sub_domain=f"etcdqs-{kubernetes_node.wid}",
                ).config.chart_config.domain
                etcd_domain = f"https://{domain}:2379"

                j.logger.info(f"Authenticate etcd with username and password")
                rc, out, err = j.sals.process.execute(
                    f"export ETCDCTL_API=3 && etcdctl --endpoints={etcd_domain} user add root:{etcd_secret} --interactive=false && etcdctl --endpoints={etcd_domain} auth enable"
                )
                j.logger.debug(f"Authentication results: {rc}, {out}, {err}")

            endpoints = [etcd_domain]
            prefix = j.sals.fs.basename(mount_location)
            if not self.zstor_config:
                self.zstor_config = self.update_zstor_config(endpoints, prefix, etcd_secret)
            ssh_client.sshclient.run(f"sudo echo '''{self.zstor_config}''' > {ZSTORCONF_PATH}")

            j.logger.info(f"Starting zdb & zdbfs on: {kubernetes_node.wid}")
            zdb_cmd_args = "--datasize $((32 * 1024 * 1024)) --mode seq --hook /home/rancher/0-db-fs/zdb_hook.sh --data /zdb/data --index /zdb/index"
            self._create_service("zdb", "/usr/bin/zdb", zdb_cmd_args, ssh_client)
            j.sals.nettools.wait_connection_test(kubernetes_node.ip_address, 9900, timeout=10)
            j.logger.info(f"ZDB is running on: {kubernetes_node.wid}")

            j.logger.info(f"Configuring ZDB on: {kubernetes_node.wid}")

            rc, out, err = j.sals.process.execute(
                dedent(
                    f"""\
                    cat << EOF | redis-cli -h {kubernetes_node.ip_address} -p 9900
                    NSNEW zdbfs-meta
                    NSNEW zdbfs-data
                    NSNEW zdbfs-temp
                    NSSET zdbfs-temp password hello
                    NSSET zdbfs-temp public 0
                    EOF
                """
                )
            )
            j.logger.debug(f"Configured zdb on {kubernetes_node.wid} with result: {rc}, {out}, {err}")
            self._create_service(
                f"zdbfs-{mount_location.replace('/', '-').replace('~', '-')}",
                "/usr/bin/zdbfs",
                f"{mount_location} -o allow_other",
                ssh_client,
            )
            j.logger.info(f"ZDBFS is running on: {kubernetes_node.wid} on mount location: {mount_location}")
        return self.zstor_config

    def _create_service(self, svc_name, command, command_args, ssh_client):
        template = f"""#!/sbin/openrc-run
        supervisor=supervise-daemon
        name="{svc_name}"
        command="{command}"
        command_args="{command_args} > /var/log/{svc_name}.log 2>&1"
        output_log="/var/log/{svc_name}.log"
        error_log="/var/log/{svc_name}.log"
        pidfile="/var/run/{svc_name}.pid"
        command_background=true
        """
        template = dedent(template)
        rc, out, err = ssh_client.sshclient.run(
            f"sudo touch /etc/init.d/{svc_name} && sudo chmod 777 /etc/init.d/{svc_name} &&  echo '{template}' > /etc/init.d/{svc_name} && sudo rc-service {svc_name} start",
            warn=True,
        )
        if rc != 0:
            j.exceptions.Runtime(f"failed to run service {svc_name}. rc: {rc}, out: {out}, err: {err}")

    def stop(self, mount_location="/home/rancher/mounted"):
        for kubernetes_node in self.vdc.kubernetes:
            ssh_client = self.vdc.get_ssh_client(
                f"qs_init_{kubernetes_node.wid}", kubernetes_node.ip_address, "rancher"
            )
            try:
                ssh_client.sshclient.run(
                    f"sudo rc-service zdbfs-{mount_location.replace('/', '-').replace('~', '-')} stop"
                )
            except Exception as e:
                j.logger.warning(f"failed to kill zdbfs to {str(e)}, killing it manually on {kubernetes_node.wid}")
                ssh_client.sshclient.run("sudo pkill -9 zdbfs")

            try:
                j.logger.info(f"Verifying to umount {mount_location} on {kubernetes_node.wid}")
                ssh_client.sshclient.run(f"sudo umount {mount_location}")
            except Exception as e:
                j.logger.warning(
                    f"failed to umount {mount_location} on {kubernetes_node.wid} or it was unmounted already"
                )

    def kill_zdb(self):
        for kubernetes_node in self.vdc.kubernetes:
            ssh_client = self.vdc.get_ssh_client(
                f"qs_init_{kubernetes_node.wid}", kubernetes_node.ip_address, "rancher"
            )
            try:
                ssh_client.sshclient.run("sudo rc-service zdb stop")
            except Exception as e:
                j.logger.warning(f"failed to kill zdb to {str(e)}, killing it manually on {kubernetes_node.wid}")
                ssh_client.sshclient.run("sudo pkill -9 zdb")
