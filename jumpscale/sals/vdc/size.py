from enum import Enum
from jumpscale.loader import j

S3_NO_DATA_NODES = 4
S3_NO_PARITY_NODES = 2
MINIO_CPU = 2
MINIO_MEMORY = 4 * 1024  # in MB
MINIO_DISK = 4 * 1024  # in MB
ZDB_STARTING_SIZE = 10  # in GB

THREEBOT_CPU = 1
THREEBOT_MEMORY = 2 * 1024  # in MB
THREEBOT_DISK = 2 * 1024  # in MB

S3_AUTO_TOPUP_FARMS = ["lochristi_dev_lab", "lochristi_dev_lab"]
ZDB_FARMS = ["lochristi_dev_lab", "lochristi_dev_lab"]
PREFERED_FARM = "lochristi_dev_lab"
NETWORK_FARM = "lochristi_dev_lab"


def _convert_eur_to_tft(amount):
    c = j.clients.liquid.get("vdc")
    eur_btc_price = c.get_pair_price("BTCEUR")
    tft_eur_price = c.get_pair_price("TFTBTC")
    eur_to_tft = 1 / (tft_eur_price.ask * eur_btc_price.ask)
    return eur_to_tft * amount


def get_vdc_tft_price(flavor):
    if isinstance(flavor, str):
        flavor = VDCFlavor[flavor.upper()]
    amount = VDC_FLAFORS[flavor]["price"]
    return _convert_eur_to_tft(amount)


def get_kubernetes_tft_price(flavor):
    if isinstance(flavor, str):
        flavor = K8SNodeFlavor[flavor.upper()]
    amount = K8S_PRICES[flavor]
    return _convert_eur_to_tft(amount)


class K8SNodeFlavor(Enum):
    SMALL = 15
    MEDIUM = 16
    BIG = 17


K8S_PRICES = {
    K8SNodeFlavor.SMALL: 5,
    K8SNodeFlavor.MEDIUM: 10,
    K8SNodeFlavor.BIG: 20,
}


K8S_SIZES = {
    K8SNodeFlavor.SMALL: {"cru": 1, "mru": 2, "sru": 25},
    K8SNodeFlavor.MEDIUM: {"cru": 2, "mru": 4, "sru": 50},
    K8SNodeFlavor.BIG: {"cru": 4, "mru": 8, "sru": 50},
}


class S3ZDBSize(Enum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3


S3_ZDB_SIZES = {
    S3ZDBSize.SMALL: {"sru": 3 * 1024},
    S3ZDBSize.MEDIUM: {"sru": 10 * 1024},
    S3ZDBSize.BIG: {"sru": 20 * 1024},
}


class VDCFlavor(Enum):
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


VDC_FLAFORS = {
    VDCFlavor.SILVER: {
        "k8s": {"no_nodes": 1, "size": K8SNodeFlavor.SMALL, "dedicated": False},
        "s3": {"size": S3ZDBSize.SMALL},
        "duration": 30,  # days
        "price": 30,
    },
    VDCFlavor.GOLD: {
        "k8s": {"no_nodes": 2, "size": K8SNodeFlavor.MEDIUM, "dedicated": False},
        "s3": {"size": S3ZDBSize.MEDIUM},
        "duration": 30,  # days
        "price": 60,
    },
    VDCFlavor.PLATINUM: {
        "k8s": {"no_nodes": 2, "size": K8SNodeFlavor.BIG, "dedicated": True},
        "s3": {"size": S3ZDBSize.BIG},
        "duration": 30,  # days
        "price": 250,
    },
}
