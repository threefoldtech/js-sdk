from gevent import monkey

monkey.patch_all(subprocess=False)  # noqa: E402

import os
from jumpscale.loader import j
from jumpscale.sals.vdc.deployer import VDC_IDENTITY_FORMAT

"""
minimal entrypoint for a 3bot container to run as part of VDC deployments on k8s


Required env variables:
- VDC_NAME  -> for identity generation
- VDC_UUID  -> for vdc workload identification
- VDC_OWNER_TNAME  -> for identity generation
- VDC_EMAIL ->  for identity generation
- VDC_PASSWORD_HASH  -> for identity generation
- EXPLORER_URL  -> for identity generation and wallet network
- VDC_WALLET_SECRET  -> for auto-top up
- VDC_MINIO_ADDRESS  -> used for monitoring to trigger auto-top up and reconfig
- VDC_S3_MAX_STORAGE  -> used for auto top up
- S3_AUTO_TOPUP_FARMS  -> used for auto top up


Role:
1- define the identity
2- import wallet
3- run auto-top up service
"""

VDC_NAME = os.environ.get("VDC_NAME")
VDC_UUID = os.environ.get("VDC_UUID")
VDC_OWNER_TNAME = os.environ.get("VDC_OWNER_TNAME")
VDC_EMAIL = os.environ.get("VDC_EMAIL")
VDC_PASSWORD_HASH = os.environ.get("VDC_PASSWORD_HASH")
EXPLORER_URL = os.environ.get("EXPLORER_URL")
VDC_WALLET_SECRET = os.environ.get("VDC_WALLET_SECRET")
VDC_S3_MAX_STORAGE = os.environ.get("VDC_S3_MAX_STORAGE")
S3_AUTO_TOPUP_FARMS = os.environ.get("S3_AUTO_TOPUP_FARMS")
VDC_MINIO_ADDRESS = os.environ.get("VDC_MINIO_ADDRESS")


VDC_VARS = {
    "VDC_NAME": VDC_NAME,
    "VDC_UUID": VDC_UUID,
    "VDC_OWNER_TNAME": VDC_OWNER_TNAME,
    "VDC_EMAIL": VDC_EMAIL,
    "VDC_PASSWORD_HASH": VDC_PASSWORD_HASH,
    "EXPLORER_URL": EXPLORER_URL,
    "VDC_WALLET_SECRET": VDC_WALLET_SECRET,
    "VDC_S3_MAX_STORAGE": VDC_S3_MAX_STORAGE,
    "S3_AUTO_TOPUP_FARMS": S3_AUTO_TOPUP_FARMS,
    "VDC_MINIO_ADDRESS": VDC_MINIO_ADDRESS,
}

if not all(list(VDC_VARS.values())):
    raise j.exceptions.Validation("MISSING ENVIRONMENT VARIABLES")


for key, value in VDC_VARS.items():
    j.sals.process.execute(f"""echo "{key}={value}" >> /etc/environment""")


username = VDC_IDENTITY_FORMAT.format(VDC_OWNER_TNAME, VDC_NAME)
words = j.data.encryption.key_to_mnemonic(VDC_PASSWORD_HASH.encode())

identity = j.core.identity.get(username, tname=username, email=VDC_EMAIL, words=words, explorer_url=EXPLORER_URL)

identity.register()
identity.save()
identity.set_default()

network = "STD"

if "testnet" in EXPLORER_URL:
    network = "TEST"

wallet = j.clients.stellar.new(name=VDC_NAME, secret=VDC_WALLET_SECRET, network=network)
wallet.save()

j.core.config.set(
    "S3_AUTO_TOP_SOLUTIONS",
    {
        "farm_names": S3_AUTO_TOPUP_FARMS.split(","),
        "extension_size": 10,
        "max_storage": int(VDC_S3_MAX_STORAGE),
        "threshold": 0.7,
        "clear_threshold": 0.4,
        "targets": {
            VDC_NAME: {
                "minio_api_url": f"http://{VDC_MINIO_ADDRESS}:9000",
                "healing_url": f"http://{VDC_MINIO_ADDRESS}:9010",
            }
        },
    },
)

j.servers.threebot.start_default(wait=True)
