from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed
from .base_component import VDCBaseComponent
from .size import (
    THREEBOT_CPU,
    THREEBOT_MEMORY,
    THREEBOT_DISK,
    VDC_SIZE,
    S3_AUTO_TOPUP_FARMS,
    S3_NO_DATA_NODES,
    S3_NO_PARITY_NODES,
)
from jumpscale.loader import j
from .scheduler import Scheduler
from jumpscale.sals.reservation_chatflow import deployer
from .proxy import VDC_PARENT_DOMAIN
from .namemanager import NameManager
import os
import uuid
import random

THREEBOT_FLIST = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest.flist"
THREEBOT_TRC_FLIST = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-js-sdk-latest_trc.flist"


class VDCThreebotDeployer(VDCBaseComponent):
    def deploy_threebot(self, minio_wid, pool_id, kube_config, embed_trc=True):
        flist = THREEBOT_TRC_FLIST if embed_trc else THREEBOT_FLIST
        # workload = self.zos.workloads.get(minio_wid)
        # if workload.info.workload_type != WorkloadType.Container:
        #     raise j.exceptions.Validation(f"workload {minio_wid} is not container workload")
        # minio_ip_address = workload.network_connection[0].ipaddress
        vdc_dict = self.vdc_instance.to_dict()
        vdc_dict.pop("s3", None)
        vdc_dict.pop("kubernetes", None)
        vdc_dict.pop("threebot", None)
        secret_env = {
            "VDC_OWNER_TNAME": self.vdc_deployer.tname,
            "VDC_EMAIL": self.vdc_deployer.email,
            "VDC_PASSWORD_HASH": self.vdc_deployer.password_hash,
            "KUBE_CONFIG": kube_config,
            "PROVISIONING_WALLET_SECRET": self.vdc_deployer.vdc_instance.provision_wallet.secret,
            "PREPAID_WALLET_SECRET": self.vdc_deployer.vdc_instance.prepaid_wallet.secret,
            "VDC_INSTANCE": j.data.serializers.json.dumps(vdc_dict),
            "THREEBOT_PRIVATE_KEY": self.vdc_deployer.threebot.private_key,
        }
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
            "S3_AUTO_TOPUP_FARMS": ",".join(S3_AUTO_TOPUP_FARMS.get()),
            # "VDC_MINIO_ADDRESS": minio_ip_address,
            "SDK_VERSION": "development_vdc",  # TODO: change when merged
            "SSHKEY": self.vdc_deployer.ssh_key.public_key.strip(),
            "MINIMAL": "true",
            "TEST_CERT": "true" if j.core.config.get("TEST_CERT") else "false",
            "ACME_SERVER_URL": j.core.config.get("VDC_ACME_SERVER_URL", "https://ca1.grid.tf"),
        }
        if embed_trc:
            _, secret, remote = self._prepare_proxy()
            if not remote:
                return
            remote_ip, remote_port = remote.split(":")
            env.update(
                {
                    "REMOTE_IP": remote_ip,
                    "REMOTE_PORT": remote_port,
                }
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
                    self.vdc_deployer.error(f"failed to deploy network on node {node.node_id}")
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
                f"reserving proxy on gateway {gateway.node_id} for subdomain: {subdomain} wid: {wid}"
            )
            try:
                success = deployer.wait_workload(wid, self.bot, expiry=5, identity_name=self.identity.instance_name)
                if not success:
                    raise DeploymentFailed()
            except DeploymentFailed:
                self.vdc_deployer.error(f"failed to deploy reverse proxy on gateway: {gateway.node_id} wid: {wid}")
                continue

            remote = f"{gateway.dns_nameserver[0]}:{gateway.tcp_router_port}"
        if not remote:
            self.vdc_deployer.error(f"all tries to reseve a proxy on pool: {gateway_pool_id} has failed")
        return subdomain, secret, remote
