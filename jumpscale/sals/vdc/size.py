from enum import Enum
from jumpscale.loader import j

# TODO: set to 6 + 4 when merging to development
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


class VDCSize:
    _LAST_LOADED = None

    def __init__(self):
        self.K8SNodeFlavor = None
        self.K8S_PRICES = None
        self.K8S_SIZES = None
        self.S3ZDBSize = None
        self.S3_ZDB_SIZES = None
        self.VDCFlavor = None
        self.VDC_FLAVORS = None

    @staticmethod
    def _convert_eur_to_tft(amount):
        c = j.clients.liquid.get("vdc")
        eur_btc_price = c.get_pair_price("BTCEUR")
        tft_eur_price = c.get_pair_price("TFTBTC")
        eur_to_tft = 1 / (tft_eur_price.ask * eur_btc_price.ask)
        return eur_to_tft * amount

    def get_vdc_tft_price(self, flavor):
        if isinstance(flavor, str):
            flavor = self.VDCFlavor[flavor.upper()]
        amount = self.VDC_FLAVORS[flavor]["price"]
        return self._convert_eur_to_tft(amount)

    def get_kubernetes_tft_price(self, flavor):
        if isinstance(flavor, str):
            flavor = self.K8SNodeFlavor[flavor.upper()]
        amount = self.K8S_PRICES[flavor]
        return self._convert_eur_to_tft(amount)

    def load(self):
        update_flag = False
        if not self._LAST_LOADED:
            update_flag = True
        elif self._LAST_LOADED < j.data.time.now() + (24 * 60 * 60):
            update_flag = True
        if update_flag:
            self.load_k8s_flavor()
            self.load_k8s_prices()
            self.load_k8s_sizes()
            self.load_s3_zdb_size()
            self.load_s3_zdb_size_details()
            self.load_vdc_flavors()
            self.load_vdc_plans()

    def load_k8s_flavor(self):
        # fills K8SNodeFlavor
        self.K8SNodeFlavor = Enum("K8SNodeFlavor", {"SMALL": 15, "MEDIUM": 16, "BIG": 17,})

    def load_k8s_prices(self):
        # fills K8S_PRICES
        self.K8S_PRICES = {self.K8SNodeFlavor.SMALL: 5, self.K8SNodeFlavor.MEDIUM: 10, self.K8SNodeFlavor.BIG: 20}

    def load_k8s_sizes(self):
        # fills K8S_SIZES
        self.K8S_SIZES = {
            self.K8SNodeFlavor.SMALL: {"cru": 1, "mru": 2, "sru": 25},
            self.K8SNodeFlavor.MEDIUM: {"cru": 2, "mru": 4, "sru": 50},
            self.K8SNodeFlavor.BIG: {"cru": 4, "mru": 8, "sru": 50},
        }

    def load_s3_zdb_size(self):
        # fills S3ZDBSize
        self.S3ZDBSize = Enum("S3ZDBSize", {"SMALL": 1, "MEDIUM": 2, "BIG": 3,})

    def load_s3_zdb_size_details(self):
        # fills S3_ZDB_SIZES
        self.S3_ZDB_SIZES = {
            self.S3ZDBSize.SMALL: {"sru": 3 * 1024},
            self.S3ZDBSize.MEDIUM: {"sru": 10 * 1024},
            self.S3ZDBSize.BIG: {"sru": 20 * 1024},
        }

    def load_vdc_flavors(self):
        # fills VDCFlavor
        self.VDCFlavor = Enum("VDCFlavor", {"SILVER": "silver", "GOLD": "gold", "PLATINUM": "platinum",})

    def load_vdc_plans(self):
        # fills VDC_FLAVORS
        self.VDC_FLAVORS = {
            self.VDCFlavor.SILVER: {
                "k8s": {
                    "no_nodes": 1,
                    "size": self.K8SNodeFlavor.SMALL,
                    "controller_size": self.K8SNodeFlavor.SMALL,
                    "dedicated": False,
                },
                "s3": {"size": self.S3ZDBSize.SMALL},
                "duration": 30,  # days
                "price": 30,
            },
            self.VDCFlavor.GOLD: {
                "k8s": {
                    "no_nodes": 2,
                    "size": self.K8SNodeFlavor.MEDIUM,
                    "controller_size": self.K8SNodeFlavor.MEDIUM,
                    "dedicated": False,
                },
                "s3": {"size": self.S3ZDBSize.MEDIUM},
                "duration": 30,  # days
                "price": 60,
            },
            self.VDCFlavor.PLATINUM: {
                "k8s": {
                    "no_nodes": 2,
                    "size": self.K8SNodeFlavor.BIG,
                    "controller_size": self.K8SNodeFlavor.BIG,
                    "dedicated": True,
                },
                "s3": {"size": self.S3ZDBSize.BIG},
                "duration": 30,  # days
                "price": 250,
            },
        }


VDC_SIZE = VDCSize()
VDC_SIZE.load()
