from gevent import monkey

monkey.patch_all(subprocess=False)  # noqa: E402

import os
from jumpscale.loader import j
from jumpscale.sals.vdc.deployer import VDC_IDENTITY_FORMAT
import gevent
import toml

"""
minimal entrypoint for a 3bot container to run as part of VDC deployments on k8s


Required env variables:
- VDC_NAME  -> for identity generation
- VDC_UUID  -> for VDC workload identification
- VDC_OWNER_TNAME  -> for identity generation
- VDC_EMAIL ->  for identity generation


- VDC_PASSWORD_HASH  -> for identity generation
- EXPLORER_URL  -> for identity generation and wallet network
- VDC_MINIO_ADDRESS  -> used for monitoring to trigger auto-top up and reconfig
- VDC_S3_MAX_STORAGE  -> used for auto top up
- S3_AUTO_TOPUP_FARMS  -> used for auto top up
- VDC_INSTANCE -> json string from the VDC instance on deployer
- PREPAID_WALLET_SECRET -> secret for prepaid wallet
- PROVISIONING_WALLET_SECRET -> secret for provisioning wallet
- ACME_SERVER_URL -> to use for package certificate
- THREEBOT_PRIVATE_KEY -> private key to be set on threebot
- BACKUP_CONFIG -> dict containing url, region, bucket, ak, sk


Role:
1- define the identity
2- import wallet
3- run auto-top up service
"""

VDC_PASSWORD_HASH = os.environ.get("VDC_PASSWORD_HASH")
EXPLORER_URL = os.environ.get("EXPLORER_URL")
VDC_S3_MAX_STORAGE = os.environ.get("VDC_S3_MAX_STORAGE")
S3_AUTO_TOPUP_FARMS = os.environ.get("S3_AUTO_TOPUP_FARMS")
VDC_MINIO_ADDRESS = os.environ.get("VDC_MINIO_ADDRESS")
MONITORING_SERVER_URL = os.environ.get("MONITORING_SERVER_URL")
TEST_CERT = os.environ.get("TEST_CERT", "false")
VDC_INSTANCE = os.environ.get("VDC_INSTANCE")
VDC_EMAIL = os.environ.get("VDC_EMAIL")
KUBE_CONFIG = os.environ.get("KUBE_CONFIG")
PROVISIONING_WALLET_SECRET = os.environ.get("PROVISIONING_WALLET_SECRET")
PREPAID_WALLET_SECRET = os.environ.get("PREPAID_WALLET_SECRET")
ACME_SERVER_URL = os.environ.get("ACME_SERVER_URL")
THREEBOT_PRIVATE_KEY = os.environ.get("THREEBOT_PRIVATE_KEY")
BACKUP_CONFIG = os.environ.get("BACKUP_CONFIG", "{}")


vdc_dict = j.data.serializers.json.loads(VDC_INSTANCE)

if not j.sals.vdc.list_all():
    vdc = j.sals.vdc.from_dict(vdc_dict)
else:
    vdc = j.sals.vdc.find(list(j.sals.vdc.list_all())[0])

VDC_INSTANCE_NAME = vdc.instance_name
os.environ.putenv("VDC_INSTANCE_NAME", VDC_INSTANCE_NAME)

VDC_VARS = {
    "VDC_PASSWORD_HASH": VDC_PASSWORD_HASH,
    "EXPLORER_URL": EXPLORER_URL,
    "VDC_S3_MAX_STORAGE": VDC_S3_MAX_STORAGE,
    "S3_AUTO_TOPUP_FARMS": S3_AUTO_TOPUP_FARMS,
    "VDC_MINIO_ADDRESS": VDC_MINIO_ADDRESS,
    "MONITORING_SERVER_URL": MONITORING_SERVER_URL,
    "TEST_CERT": TEST_CERT,
    "VDC_INSTANCE": VDC_INSTANCE,
    "VDC_EMAIL": VDC_EMAIL,
    "KUBE_CONFIG": KUBE_CONFIG,
    "PROVISIONING_WALLET_SECRET": os.environ.get("PROVISIONING_WALLET_SECRET"),
    "PREPAID_WALLET_SECRET": os.environ.get("PREPAID_WALLET_SECRET"),
    "VDC_INSTANCE_NAME": VDC_INSTANCE_NAME,
    "SDK_VERSION": os.environ.get("SDK_VERSION", "development"),
    "BACKUP_CONFIG": BACKUP_CONFIG,
}


for key, value in VDC_VARS.items():
    # TODO: bring back when merging to development branch
    # if not value:
    #     raise j.exceptions.Validation(f"MISSING ENVIRONMENT VARIABLES. {key} is not set")
    j.sals.process.execute(f"""echo "{key}='{value}'" >> /root/.bashrc""")


username = VDC_IDENTITY_FORMAT.format(vdc_dict["owner_tname"], vdc_dict["vdc_name"], vdc_dict["solution_uuid"])
words = j.data.encryption.key_to_mnemonic(VDC_PASSWORD_HASH.encode())

identity = j.core.identity.get(
    f"vdc_ident_{vdc_dict['solution_uuid']}", tname=username, email=VDC_EMAIL, words=words, explorer_url=EXPLORER_URL
)

identity.register()
identity.save()
identity.set_default()

network = "STD"

j.core.config.set(
    "S3_AUTO_TOP_SOLUTIONS",
    {
        "farm_names": S3_AUTO_TOPUP_FARMS.split(","),
        "extension_size": 10,
        "max_storage": int(VDC_S3_MAX_STORAGE),
        "threshold": 0.7,
        "clear_threshold": 0.4,
        "targets": {
            vdc.vdc_name: {
                "minio_api_url": f"http://{VDC_MINIO_ADDRESS}:9000",
                "healing_url": f"http://{VDC_MINIO_ADDRESS}:9010",
            }
        },
    },
)


j.core.config.set("VDC_THREEBOT", True)

j.config.set("SEND_REMOTE_ALERTS", True)

# TODO: remove empty exception when merging with development branch
try:
    from register_dashboard import register_dashboard

    register_dashboard()
except:
    pass

deadline = j.data.time.now().timestamp + 10 * 60
while not vdc.threebot.domain and j.data.time.now().timestamp < deadline:
    j.logger.info("wating for threebot domain reservation")
    vdc.load_info()
    gevent.sleep(10)

j.core.config.set("OVER_PROVISIONING", True)
server = j.servers.threebot.get("default")
server.packages.add("/sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/billing")
if TEST_CERT != "true":
    package_config = toml.load(
        "/sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/vdc_dashboard/package.toml"
    )
    package_config["servers"][0]["domain"] = vdc.threebot.domain
    with open("/sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/vdc_dashboard/package.toml", "w") as f:
        toml.dump(package_config, f)
    if ACME_SERVER_URL:
        server.acme_server_type = "custom"
        server.acme_server_url = ACME_SERVER_URL

server.packages.add(
    "/sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/vdc_dashboard", admins=[f"{vdc.owner_tname}.3bot"]
)
server.save()

j.sals.process.execute("cat /root/.ssh/authorized_keys > /root/.ssh/id_rsa.pub")
j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/kube/{vdc.owner_tname}")
j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/kube/{vdc.owner_tname}/{vdc.vdc_name}.yaml", KUBE_CONFIG)

j.sals.fs.mkdirs("/root/.kube")
j.sals.fs.write_file("/root/.kube/config", KUBE_CONFIG)

# backup config and restore
# install velero
try:
    BACKUP_CONFIG = j.data.serializers.json.loads(BACKUP_CONFIG)
    ak = BACKUP_CONFIG.get("ak")
    sk = BACKUP_CONFIG.get("sk")
    url = BACKUP_CONFIG.get("url")
    region = BACKUP_CONFIG.get("region")
    bucket = BACKUP_CONFIG.get("bucket")
    if all([ak, sk, url, region]):
        j.sals.fs.write_file(
            "/root/credentials",
            f"""
        [default]
        aws_access_key_id={ak}
        aws_secret_access_key={sk}
        """,
        )
        j.sals.process.execute(
            f"/sbin/velero install --provider aws --use-restic --plugins velero/velero-plugin-for-aws:v1.1.0 --bucket {bucket} --secret-file /root/credentials --backup-location-config region={region},s3ForcePathStyle=true,s3Url={url}",
            showout=True,
        )

        # get and restore latest backup
        ret, out, _ = j.sals.process.execute("/sbin/velero backup get -o json", showout=True)
        if out:
            backups = j.data.serializers.json.loads(out)
            backup_name = ""
            if len(backups.get("items", [])) > 0:
                backup_name = backups["items"][0].get("metadata", {}).get("name")
            if backup_name:
                j.sals.process.execute(
                    f"/sbin/velero restore create restore-{backup_name}-{j.data.time.utcnow().timestamp} --from-backup {backup_name}",
                    showout=True,
                )

        # create backup schedule for automatic backups
        j.sals.process.execute(
            '/sbin/velero create schedule vdc --schedule="@every 24h" -l "backupType=vdc"', showout=True
        )

        # redeploy subdomain
        try:
            from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_all_vdc_deployments

            public_ip = vdc.kubernetes[0].public_ip
            zos = j.sals.zos.get()
            gateways = zos.gateways_finder.gateways_search()
            domain_mapping = {}
            wids = []
            for gw in gateways:
                if not gw.managed_domains:
                    continue
                domain_mapping.update({dom: gw for dom in gw.managed_domains})
            all_pools = zos.pools.list()
            node_mapping = {}
            for pool in all_pools:
                node_mapping.update({node_id: pool.pool_id for node_id in pool.node_ids})
            domains_deployed = set()
            deployments = get_all_vdc_deployments(vdc.vdc_name)
            for deployment in deployments:
                domain_name = deployment.get("Domain")
                if not domain_name:
                    continue
                if domain_name in domains_deployed:
                    continue
                try:
                    parent_domain = ".".join(domain_name.split(".")[1:])
                    gw = domain_mapping.get(parent_domain)
                    if not gw:
                        j.logger.warning(f"unable to get the gateway that managed this domain {domain_name}")
                        continue
                    pool_id = node_mapping.get(gw.node_id)
                    if not pool_id:
                        farm_name = zos._explorer.farms.get(gw.farm_id).name
                        pool = zos.pools.create(0, 0, 0, farm_name)
                        pool = zos.pools.get(pool.reservation_id)
                        node_mapping.update({node_id: pool.pool_id for node_id in pool.node_ids})
                        pool_id = pool.pool_id
                    domain = zos.gateway.sub_domain(gw.node_id, domain_name, [public_ip], pool_id)
                    wids.append(zos.workloads.deploy(domain))
                    domains_deployed.add(domain_name)
                except Exception as e:
                    j.logger.critical(f"failed to redeploy domain {domain_name} due to error {str(e)}")

            for wid in wids:
                try:
                    success = zos.workloads.wait(wid, 1)
                    if not success:
                        j.logger.critical(f"subdomain of wid: {wid} failed to redeploy")
                except Exception as e:
                    j.logger.critical(f"subdomain of wid: {wid} failed to redeploy due to error {str(e)}")
            # TODO: how to re-invoke ingress/deployment to regenrate certs
        except Exception as e:
            j.logger.error(f"couldn't restore subdomains due to error {str(e)}")
except Exception as e:
    j.logger.error(f"backup config failed due to error {str(e)}")

# Register provisioning and prepaid wallets

wallet = j.clients.stellar.get(
    name=f"prepaid_wallet_{vdc.solution_uuid}", secret=PREPAID_WALLET_SECRET, network=network
)
wallet.save()

wallet = j.clients.stellar.get(
    name=f"provision_wallet_{vdc.solution_uuid}", secret=PROVISIONING_WALLET_SECRET, network=network
)
wallet.save()
if THREEBOT_PRIVATE_KEY:
    with open("/root/.ssh/id_rsa", "w") as f:
        f.writelines(THREEBOT_PRIVATE_KEY)
    j.sals.fs.chmod("/root/.ssh/id_rsa", 0o600)
