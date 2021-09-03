from gevent import monkey

monkey.patch_all(subprocess=False)  # noqa: E402

import os
from jumpscale.loader import j
from jumpscale.sals.vdc.deployer import VDC_IDENTITY_FORMAT
import gevent
import toml
import hashlib

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
- NETWORK_FARMS -> used for deploying extra workers with public ip
- COMPUTE_FARMS -> used for deploying extra workers
- VDC_INSTANCE -> json string from the VDC instance on deployer
- PREPAID_WALLET_SECRET -> secret for prepaid wallet
- PROVISIONING_WALLET_SECRET -> secret for provisioning wallet
- ACME_SERVER_URL -> to use for package certificate
- THREEBOT_PRIVATE_KEY -> private key to be set on threebot
- BACKUP_CONFIG -> dict containing url, region, bucket, ak, sk
- S3_URL
- S3_BUCKET
- S3_AK
- S3_SK


Role:
1- define the identity
2- import wallet
3- run auto-top up service
"""

VDC_PASSWORD_HASH = os.environ.get("VDC_PASSWORD_HASH")
EXPLORER_URL = os.environ.get("EXPLORER_URL")
VDC_S3_MAX_STORAGE = os.environ.get("VDC_S3_MAX_STORAGE")
S3_AUTO_TOPUP_FARMS = os.environ.get("S3_AUTO_TOPUP_FARMS")
NETWORK_FARMS = os.environ.get("NETWORK_FARMS")
COMPUTE_FARMS = os.environ.get("COMPUTE_FARMS")
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
S3_URL = os.environ.get("S3_URL", "")
S3_BUCKET = os.environ.get("S3_BUCKET", "")
S3_AK = os.environ.get("S3_AK", "")
S3_SK = os.environ.get("S3_SK", "")


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
    "NETWORK_FARMS": NETWORK_FARMS,
    "COMPUTE_FARMS": COMPUTE_FARMS,
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
    "THREEBOT_PRIVATE_KEY": THREEBOT_PRIVATE_KEY,
    "S3_URL": S3_URL,
    "S3_AK": S3_AK,
    "S3_SK": S3_SK,
    "S3_BUCKET": S3_BUCKET,
    "CERT": os.environ.get("CERT", ""),
    "CERT_PRIVATE_KEY": os.environ.get("CERT_PRIVATE_KEY", ""),
    "CERT_FULLCHAIN": os.environ.get("CERT_FULLCHAIN", ""),
}


for key, value in VDC_VARS.items():
    # TODO: bring back when merging to development branch
    # if not value:
    #     raise j.exceptions.Validation(f"MISSING ENVIRONMENT VARIABLES. {key} is not set")
    j.sals.process.execute(f"""echo "export {key}='{value}'" >> /root/.bashrc""")


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

if NETWORK_FARMS:
    j.core.config.set("NETWORK_FARMS", NETWORK_FARMS.split(","))

if COMPUTE_FARMS:
    j.core.config.set("COMPUTE_FARMS", COMPUTE_FARMS.split(","))

j.core.config.set("VDC_THREEBOT", True)

j.config.set("SEND_REMOTE_ALERTS", True)

# TODO: remove empty exception when merging with development branch
try:
    from register_dashboard import register_dashboard

    register_dashboard()
except:
    pass

deadline = j.data.time.now().timestamp + 10 * 60
vdc.load_info()
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

    if VDC_VARS.get("CERT"):
        certs_path = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "certs")
        cert_path = j.sals.fs.join_paths(certs_path, "cert.pem")
        key_path = j.sals.fs.join_paths(certs_path, "key.pem")
        fullchain_path = j.sals.fs.join_paths(certs_path, "fullchain.pem")

        j.sals.fs.makedirs(certs_path)
        j.sals.fs.write_file(cert_path, VDC_VARS["CERT"])
        j.sals.fs.write_file(key_path, VDC_VARS["CERT_PRIVATE_KEY"])
        j.sals.fs.write_file(fullchain_path, VDC_VARS["CERT_FULLCHAIN"])

        package_config["servers"][0]["cert_path"] = cert_path
        package_config["servers"][0]["key_path"] = key_path
        package_config["servers"][0]["fullchain_path"] = fullchain_path
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
j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/keys/{vdc.owner_tname}/{vdc.vdc_name}")
j.sals.process.execute(
    f"cat /root/.ssh/authorized_keys > {j.core.dirs.CFGDIR}/vdc/keys/{vdc.owner_tname}/{vdc.vdc_name}/id_rsa.pub"
)
j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/kube/{vdc.owner_tname}")
j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/kube/{vdc.owner_tname}/{vdc.vdc_name}.yaml", KUBE_CONFIG)

j.sals.fs.mkdirs("/root/.kube")
j.sals.fs.write_file("/root/.kube/config", KUBE_CONFIG)

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
    j.sals.process.execute(
        f"cp /root/.ssh/id_rsa {j.core.dirs.CFGDIR}/vdc/keys/{vdc.owner_tname}/{vdc.vdc_name}/id_rsa"
    )


# no restore for now
# try:
#     from jumpscale.packages.vdc_dashboard.services.etcd_backup import service

#     service.job()
# except Exception as e:
#     j.logger.critical(f"failed to do initial vdc controller backup due to error: {str(e)}")

# try:
#     from jumpscale.packages.vdc_dashboard.services.domain import service

#     service.job()
# except Exception as e:
#     j.logger.critical(f"failed to do initial restore of domains due to error: {str(e)}")
