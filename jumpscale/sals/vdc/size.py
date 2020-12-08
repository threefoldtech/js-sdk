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


# TODO: use the correct url
WORKLOAD_SIZES_URL = "https://raw.githubusercontent.com/threefoldfoundation/vdc_pricing/master/workload_sizes.json"
PLANS_URL = "https://raw.githubusercontent.com/threefoldfoundation/vdc_pricing/master/plans.json"


class VDCSize:
    _LAST_LOADED = None

    def __init__(self):
        self._K8SNodeFlavor = None
        self._K8S_PRICES = None  # TODO: remove
        self._K8S_SIZES = None
        self._S3ZDBSize = None
        self._S3_ZDB_SIZES = None
        self._VDCFlavor = None
        self._VDC_FLAVORS = None
        self._workload_sizes = None
        self._plans_data = None

    @property
    def K8SNodeFlavor(self):
        if not self.is_updated:
            self.load()
        return self._K8SNodeFlavor

    @property
    def K8S_PRICES(self):
        if not self.is_updated:
            self.load()
        return self._K8S_PRICES

    @property
    def K8S_SIZES(self):
        if not self.is_updated:
            self.load()
        return self._K8S_SIZES

    @property
    def S3ZDBSize(self):
        if not self.is_updated:
            self.load()
        return self._S3ZDBSize

    @property
    def S3_ZDB_SIZES(self):
        if not self.is_updated:
            self.load()
        return self._S3_ZDB_SIZES

    @property
    def VDCFlavor(self):
        if not self.is_updated:
            self.load()
        return self._VDCFlavor

    @property
    def VDC_FLAVORS(self):
        if not self.is_updated:
            self.load()
        return self._VDC_FLAVORS

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

    @property
    def is_updated(self):
        if not self._LAST_LOADED:
            return False
        elif self._LAST_LOADED + (24 * 60 * 60) < j.data.time.now().timestamp:
            return False
        return True

    def load(self):
        self.fetch_upstream_info()
        self.load_k8s_flavor()
        self.load_k8s_sizes()
        self.load_s3_zdb_size()
        self.load_s3_zdb_size_details()
        self.load_vdc_flavors()
        self.load_vdc_plans()

    def fetch_upstream_info(self):
        self._LAST_LOADED = j.data.time.now().timestamp
        workloads_res = j.tools.http.get(WORKLOAD_SIZES_URL)
        workloads_res.raise_for_status()
        self._workload_sizes = workloads_res.json()

        plans_res = j.tools.http.get(PLANS_URL)
        plans_res.raise_for_status()
        self._plans_data = plans_res.json()

    def load_k8s_flavor(self):
        # fills K8SNodeFlavor
        values = dict()
        for key, val in self._workload_sizes["kubernetes"].items():
            values[key.upper()] = val["value"]
        self._K8SNodeFlavor = Enum("K8SNodeFlavor", values)

    def load_k8s_sizes(self):
        # fills K8S_SIZES
        self._K8S_SIZES = dict()
        for key, val in self._workload_sizes["kubernetes"].items():
            self.K8S_SIZES[self.K8SNodeFlavor[key.upper()]] = {"cru": val["cru"], "mru": val["mru"], "sru": val["sru"]}

    def load_s3_zdb_size(self):
        # fills S3ZDBSize
        values = dict()
        for key, val in self._workload_sizes["zdb"].items():
            values[key.upper()] = val["value"]
        self._S3ZDBSize = Enum("S3ZDBSize", values)

    def load_s3_zdb_size_details(self):
        # fills S3_ZDB_SIZES
        self._S3_ZDB_SIZES = dict()
        for key, val in self._workload_sizes["zdb"].items():
            self.S3_ZDB_SIZES[self.S3ZDBSize[key.upper()]] = {"sru": val["sru"]}

    def load_vdc_flavors(self):
        # fills VDCFlavor
        values = dict()
        for key in self._plans_data:
            values[key.upper()] = key
        self._VDCFlavor = Enum("VDCFlavor", values)

    def load_vdc_plans(self):
        # fills VDC_FLAVORS
        self._VDC_FLAVORS = dict()
        for key, val in self._plans_data.items():
            self.VDC_FLAVORS[self.VDCFlavor[key.upper()]] = {
                "k8s": {
                    "no_nodes": val["k8s"]["no_nodes"],
                    "size": self.K8SNodeFlavor[val["k8s"]["size"].upper()],
                    "controller_size": self.K8SNodeFlavor[val["k8s"]["controller_size"].upper()],
                    "dedicated": val["k8s"]["dedicated"],
                },
                "s3": {"size": self.S3ZDBSize[val["s3"]["size"].upper()]},
                "duration": val["duration"],
            }


VDC_SIZE = VDCSize()
