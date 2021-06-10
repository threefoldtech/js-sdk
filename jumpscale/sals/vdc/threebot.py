import datetime
import random
import uuid

import requests

from jumpscale.core.base import Base, fields
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployer
from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed

from .base_component import VDCBaseComponent
from .namemanager import NameManager
from .proxy import VDC_PARENT_DOMAIN
from .scheduler import Scheduler
from .size import (
    COMPUTE_FARMS,
    NETWORK_FARMS,
    S3_AUTO_TOPUP_FARMS,
    S3_NO_DATA_NODES,
    S3_NO_PARITY_NODES,
    THREEBOT_CPU,
    THREEBOT_DISK,
    THREEBOT_MEMORY,
    VDC_SIZE,
)

THREEBOT_FLIST = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest.flist"
THREEBOT_TRC_FLIST = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest_trc.flist"
THREEBOT_VDC_FLIST = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest_vdc.flist"

# etcd backup config can be set using
"""JS-NG> j.core.config.set("VDC_S3_CONFIG", s3_config)
JS-NG> s3_config = {"S3_URL": "https://s3.grid.tf", "S3_BUCKET": "vdc-devnet", "S3_AK": "", "S3_SK": ""}
JS-NG> """


class ThreebotCertificate(Base):
    private_key = fields.String()
    cert = fields.String()
    fullchain = fields.String()
    csr = fields.String()


class VDCThreebotDeployer(VDCBaseComponent):
    def __init__(self, *args, **kwargs):
        self._branch = None
        super().__init__(*args, **kwargs)
        self.acme_server_url = j.core.config.get("VDC_ACME_SERVER_URL", "https://ca1.grid.tf")
        self.acme_server_api_key = j.core.config.get("VDC_ACME_SERVER_API_KEY", "")

    @property
    def branch(self):
        if not self._branch:
            try:
                path = j.packages.vdc.__file__
                git_client = j.clients.git.get("default_vdc")
                git_client.path = j.tools.git.find_git_path(path)
                git_client.save()
                self._branch = git_client.branch_name
            except Exception as e:
                # won't fail unless we move the vdc deployer package
                j.logger.critical(
                    f"Using development as default branch. VDC package location is changed/courrpted, Please fix me, Error: {str(e)}"
                )
                self._branch = "development"
        return self._branch

    def get_subdomain(self):
        # TODO: parent domain should be always the same
        prefix = self.vdc_deployer.get_prefix()
        if "test" in j.core.identity.me.explorer_url:
            prefix += "test"
        elif "dev" in j.core.identity.me.explorer_url:
            prefix += "dev"
        else:
            prefix += "main"

        return f"{prefix}.{VDC_PARENT_DOMAIN}"

    def prefetch_cert(self):
        url = f"{self.acme_server_url}/api/prefetch"
        domains = [self.get_subdomain()]
        resp = requests.post(url, json={"domains": domains}, headers={"X-API-KEY": self.acme_server_api_key})
        resp.raise_for_status()
        return ThreebotCertificate.from_dict(resp.json())

    def deploy_threebot(
        self, minio_wid, pool_id, kube_config, embed_trc=True, backup_config=None, zdb_farms=None, cert=None
    ):
        open("/tmp/times", "a").write(f"TIMESTAMP: start_threebot {datetime.datetime.now()}\n")
        backup_config = backup_config or {}
        etcd_backup_config = j.core.config.get("VDC_S3_CONFIG", {})
        flist = THREEBOT_VDC_FLIST if embed_trc else THREEBOT_FLIST
        # workload = self.zos.workloads.get(minio_wid)
        # if workload.info.workload_type != WorkloadType.Container:
        #     raise j.exceptions.Validation(f"workload {minio_wid} is not container workload")
        # minio_ip_address = workload.network_connection[0].ipaddress
        vdc_dict = self.vdc_instance.to_dict()
        vdc_dict.pop("s3", None)
        vdc_dict.pop("kubernetes", None)
        vdc_dict.pop("threebot", None)
        secret_env = {
            "BACKUP_CONFIG": j.data.serializers.json.dumps(backup_config),
            "VDC_OWNER_TNAME": self.vdc_deployer.tname,
            "VDC_EMAIL": self.vdc_deployer.email,
            "VDC_PASSWORD_HASH": self.vdc_deployer.vdc_instance.get_password(),
            "KUBE_CONFIG": kube_config,
            "PROVISIONING_WALLET_SECRET": self.vdc_deployer.vdc_instance.provision_wallet.secret,
            "PREPAID_WALLET_SECRET": self.vdc_deployer.vdc_instance.prepaid_wallet.secret,
            "VDC_INSTANCE": j.data.serializers.json.dumps(vdc_dict),
            "THREEBOT_PRIVATE_KEY": self.vdc_deployer.ssh_key.private_key.strip(),
            "S3_URL": etcd_backup_config.get("S3_URL", ""),
            "S3_BUCKET": etcd_backup_config.get("S3_BUCKET", ""),
            "S3_AK": etcd_backup_config.get("S3_AK", ""),
            "S3_SK": etcd_backup_config.get("S3_SK", ""),
        }

        if cert:
            secret_env["CERT"] = cert.cert
            secret_env["CERT_PRIVATE_KEY"] = cert.private_key
            secret_env["CERT_FULLCHAIN"] = cert.fullchain

        env = {
            "VDC_NAME": self.vdc_name,
            "MONITORING_SERVER_URL": j.config.get("MONITORING_SERVER_URL", ""),
            "VDC_UUID": self.vdc_uuid,
            "EXPLORER_URL": j.core.identity.me.explorer_url,
            "VDC_S3_MAX_STORAGE": str(
                int(
                    VDC_SIZE.S3_ZDB_SIZES[VDC_SIZE.VDC_FLAVORS[self.vdc_deployer.flavor]["s3"]["size"]]["sru"]
                    * (1 + (S3_NO_PARITY_NODES / (S3_NO_DATA_NODES + S3_NO_PARITY_NODES)))
                )
            ),
            "S3_AUTO_TOPUP_FARMS": ",".join(S3_AUTO_TOPUP_FARMS.get()) if not zdb_farms else ",".join(zdb_farms),
            "NETWORK_FARMS": ",".join(NETWORK_FARMS.get()),
            "COMPUTE_FARMS": ",".join(COMPUTE_FARMS.get()),
            # "VDC_MINIO_ADDRESS": minio_ip_address,
            "SDK_VERSION": self.branch,
            "SSHKEY": self.vdc_deployer.ssh_key.public_key.strip(),
            "MINIMAL": "true",
            "TEST_CERT": "true" if j.core.config.get("TEST_CERT") else "false",
            "ACME_SERVER_URL": self.acme_server_url,
        }
        if embed_trc:
            _, secret, remote = self._prepare_proxy()
            if not remote:
                return
            remote_ip, remote_port = remote.split(":")
            env.update(
                {"REMOTE_IP": remote_ip, "REMOTE_PORT": remote_port,}
            )
            secret_env["TRC_SECRET"] = secret
        if not self.vdc_instance.kubernetes:
            self.vdc_instance.load_info()

        scheduler = Scheduler(pool_id=pool_id)
        for node in scheduler.nodes_by_capacity(THREEBOT_CPU, THREEBOT_DISK / 1024, THREEBOT_MEMORY / 1024):
            network_view = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
            self.vdc_deployer.info(f"VDC threebot: node {node.node_id} selected")
            result = deployer.add_network_node(
                network_view.name, node, pool_id, network_view, self.bot, self.identity.instance_name
            )

            self.vdc_deployer.info(f"VDC threebot network update result for node {node.node_id} is {result}")
            if result:
                network_updated = True
                try:
                    for wid in result["ids"]:
                        success = deployer.wait_workload(
                            wid,
                            self.bot,
                            expiry=5,
                            breaking_node_id=node.node_id,
                            identity_name=self.identity.instance_name,
                            cancel_by_uuid=False,
                        )
                        network_updated = network_updated and success
                    if not network_updated:
                        raise DeploymentFailed()
                except DeploymentFailed:
                    self.vdc_deployer.error(f"Failed to deploy network on node {node.node_id}")
                    continue
            network_view = network_view.copy()
            ip_address = network_view.get_free_ip(node)
            self.vdc_deployer.info(f"VDC threebot container ip address {ip_address}")
            if not ip_address:
                continue
            explorer = None
            if "test" in j.core.identity.me.explorer_url:
                explorer = "test"
            elif "dev" in j.core.identity.me.explorer_url:
                explorer = "dev"
            else:
                explorer = "main"

            log_config = j.core.config.get("VDC_LOG_CONFIG", {})
            if log_config:
                log_config["channel_name"] = f"{self.vdc_instance.instance_name}_{explorer}"

            wid = deployer.deploy_container(
                pool_id=pool_id,
                node_id=node.node_id,
                network_name=network_view.name,
                ip_address=ip_address,
                flist=flist,
                env=env,
                cpu=THREEBOT_CPU,
                memory=THREEBOT_MEMORY,
                disk_size=THREEBOT_DISK,
                secret_env=secret_env,
                identity_name=self.identity.instance_name,
                description=self.vdc_deployer.description,
                form_info={"chatflow": "threebot", "Solution name": self.vdc_name},
                solution_uuid=self.vdc_uuid,
                log_config=log_config,
            )
            self.vdc_deployer.info(f"VDC threebot container wid: {wid}")
            try:
                success = deployer.wait_workload(
                    wid, self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                )
                if success:
                    open("/tmp/times", "a").write(f"TIMESTAMP: end_threebot {datetime.datetime.now()}\n")
                    return wid
                raise DeploymentFailed()
            except DeploymentFailed:
                self.vdc_deployer.error(f"failed to deploy threebot container on node: {node.node_id} wid: {wid}")
                continue

    def _prepare_proxy(self):
        prefix = self.vdc_deployer.get_prefix()
        parent_domain = VDC_PARENT_DOMAIN
        subdomain = f"{prefix}.{parent_domain}"
        secret = f"{self.identity.tid}:{uuid.uuid4().hex}"
        gateways = self.vdc_deployer.proxy.fetch_myfarm_gateways()
        random.shuffle(gateways)
        gateway_pool_id = self.vdc_deployer.proxy.get_gateway_pool_id()
        remote = None
        domain_source = j.core.config.get("VDC_DOMAIN_SOURCE", "gateway")

        for gateway in gateways:
            # deploy subdomain
            ip_addresses = self.vdc_deployer.proxy.get_gateway_addresses(gateway)
            namemanager = NameManager(
                domain_source, gateway=gateway, pool_id=gateway_pool_id, proxy_instance=self.vdc_deployer.proxy
            )
            subdomain, subdomain_id = namemanager.create_subdomain(
                parent_domain=parent_domain, prefix=prefix, ip_addresses=ip_addresses, vdc_uuid=self.vdc_uuid
            )

            j.logger.info(f"Created subdomain successfully on {domain_source} with id: {subdomain_id}")

            # if old records exist for this prefix clean it.
            wid = deployer.create_proxy(
                gateway_pool_id,
                gateway.node_id,
                subdomain,
                secret,
                self.identity.instance_name,
                self.vdc_deployer.description,
                secret=secret,
            )
            self.vdc_deployer.info(
                f"Reserving proxy on gateway {gateway.node_id} for subdomain: {subdomain} wid: {wid}"
            )
            try:
                success = deployer.wait_workload(wid, self.bot, expiry=5, identity_name=self.identity.instance_name)
                if not success:
                    raise DeploymentFailed(f"failed to deploy reverse proxy on gateway: {gateway.node_id} wid: {wid}")
            except DeploymentFailed:
                self.vdc_deployer.error(f"Failed to deploy reverse proxy on gateway: {gateway.node_id} wid: {wid}")
                continue

            remote = f"{gateway.dns_nameserver[0]}:{gateway.tcp_router_port}"
        if not remote:
            self.vdc_deployer.error(f"All attempts to reseve a proxy on pool: {gateway_pool_id} has failed")
        return subdomain, secret, remote
