from enum import Enum
from jumpscale.loader import j


S3_NO_DATA_NODES = 6
S3_NO_PARITY_NODES = 4
MINIO_CPU = 1
MINIO_MEMORY = 1 * 1024  # in MB
MINIO_DISK = 2 * 1024  # in MB
ZDB_STARTING_SIZE = 10  # in GB

THREEBOT_CPU = 1
THREEBOT_MEMORY = 1 * 1024  # in MB
THREEBOT_DISK = 2 * 1024  # in MB

INITIAL_RESERVATION_DURATION = 1  # in hours

ETCD_CPU = 1
ETCD_MEMORY = 2 * 1024  # in MB
ETCD_DISK = 10240  # in MB
ETCD_CLUSTER_SIZE = 3


class FarmConfigBase:
    _LAST_LOADED = None
    _CONF = None
    KEY = None

    @classmethod
    def update_config(cls):
        conf_file_path = j.core.config.get("VDC_FARMS_CONFIG")
        if not conf_file_path:
            return
        if any(
            [
                cls._LAST_LOADED and cls._LAST_LOADED < j.data.time.now().timestamp - 15 * 60,
                not cls._CONF and not cls._LAST_LOADED,
            ]
        ):
            try:
                cls._CONF = j.data.serializers.json.load_from_file(conf_file_path)
            except Exception as e:
                j.logger.warning(f"Failed to load vdc farm config from path: {conf_file_path} due to error: {e}")
            cls._LAST_LOADED = j.data.time.now().timestamp

    @classmethod
    def get(cls):
        network = get_explorer_network()
        cls.update_config()
        if cls._CONF:
            val = cls._CONF.get(cls.KEY, {}).get(network)
            if val:
                return val
        return getattr(cls, network)


class S3_AUTO_TOPUP_FARMS(FarmConfigBase):
    KEY = "S3_AUTO_TOPUP_FARMS"
    devnet = ["lochristi_dev_lab", "lochristi_dev_lab"]
    testnet = ["freefarm", "freefarm"]
    mainnet = ["freefarm", "freefarm"]


class ZDB_FARMS(FarmConfigBase):
    KEY = "ZDB_FARMS"
    devnet = ["lochristi_dev_lab", "lochristi_dev_lab"]
    testnet = ["freefarm", "freefarm"]
    mainnet = ["freefarm", "freefarm"]


class COMPUTE_FARMS(FarmConfigBase):
    KEY = "COMPUTE_FARMS"
    devnet = ["lochristi_dev_lab"]
    testnet = ["freefarm"]
    mainnet = ["freefarm"]


class NETWORK_FARMS(FarmConfigBase):
    KEY = "NETWORK_FARMS"
    devnet = ["lochristi_dev_lab"]
    testnet = ["freefarm"]
    mainnet = ["freefarm"]


class PROXY_FARMS(FarmConfigBase):
    KEY = "PROXY_FARMS"
    devnet = ["csfarmer"]
    testnet = ["csfarmer"]
    mainnet = ["csfarmer"]


class FARM_DISCOUNT(FarmConfigBase):
    devnet = 0.99
    testnet = 0.9
    mainnet = 0


def get_explorer_network():
    networks = ["devnet", "testnet"]
    for net in networks:
        if net in j.core.identity.me.explorer_url:
            return net
    return "mainnet"


WORKLOAD_SIZES_URL = "https://raw.githubusercontent.com/threefoldfoundation/vdc_pricing/master/workload_sizes.json"
PLANS_URL = "https://raw.githubusercontent.com/threefoldfoundation/vdc_pricing/master/plans.json"
PRICES_URL = "https://raw.githubusercontent.com/threefoldfoundation/vdc_pricing/master/prices.json"


class VDCSize:
    def __init__(self):
        self._LAST_LOADED = None
        self._k8s_node_flavor = None
        self._k8s_sizes = None
        self._s3_zdb_size = None
        self._s3_zdb_sizes = None
        self._vdc_flavor = None
        self._vdc_flavors = None
        self._services = None
        self._prices = None
        self._workload_sizes = None
        self._plans_data = None
        self._prices_data = None

    @property
    def K8SNodeFlavor(self):
        if not self.is_updated:
            self.load()
        return self._k8s_node_flavor

    @property
    def K8S_SIZES(self):
        if not self.is_updated:
            self.load()
        return self._k8s_sizes

    @property
    def S3ZDBSize(self):
        if not self.is_updated:
            self.load()
        return self._s3_zdb_size

    @property
    def S3_ZDB_SIZES(self):
        if not self.is_updated:
            self.load()
        return self._s3_zdb_sizes

    @property
    def VDCFlavor(self):
        if not self.is_updated:
            self.load()
        return self._vdc_flavor

    @property
    def VDC_FLAVORS(self):
        if not self.is_updated:
            self.load()
        return self._vdc_flavors

    @property
    def Services(self):
        if not self.is_updated:
            self.load()
        return self._services

    @property
    def PRICES(self):
        if not self.is_updated:
            self.load()
        return self._prices

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
        self.load_services()
        self.load_prices()

    def fetch_upstream_info(self):
        j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/size")
        try:
            workloads_res = j.tools.http.get(WORKLOAD_SIZES_URL)
            workloads_res.raise_for_status()
            self._workload_sizes = workloads_res.json()
            j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/size/workload_sizes.json", workloads_res.text)
        except Exception as e:
            j.logger.warning(f"Failed to download workload_size due to error {str(e)}")
            if not j.sals.fs.exists(f"{j.core.dirs.CFGDIR}/vdc/size/workload_sizes.json"):
                raise e
            workloads_data = j.sals.fs.read_file(f"{j.core.dirs.CFGDIR}/vdc/size/workload_sizes.json")
            self._workload_sizes = j.data.serializers.json.loads(workloads_data)

        try:
            plans_res = j.tools.http.get(PLANS_URL)
            plans_res.raise_for_status()
            self._plans_data = plans_res.json()
            j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/size/plans.json", plans_res.text)
        except Exception as e:
            j.logger.warning(f"Failed to download plans_data due to error {str(e)}")
            if not j.sals.fs.exists(f"{j.core.dirs.CFGDIR}/vdc/size/plans.json"):
                raise e
            plans_data = j.sals.fs.read_file(f"{j.core.dirs.CFGDIR}/vdc/size/plans.json")
            self._plans_data = j.data.serializers.json.loads(plans_data)

        try:
            prices_res = j.tools.http.get(PRICES_URL)
            prices_res.raise_for_status()
            self._prices_data = prices_res.json()
            j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/size/prices.json", prices_res.text)
        except Exception as e:
            j.logger.warning(f"Failed to download prices due to error {str(e)}")
            if not j.sals.fs.exists(f"{j.core.dirs.CFGDIR}/vdc/size/prices.json"):
                raise e
            prices_data = j.sals.fs.read_file(f"{j.core.dirs.CFGDIR}/vdc/size/prices.json")
            self._prices_data = j.data.serializers.json.loads(prices_data)

        self._LAST_LOADED = j.data.time.now().timestamp

    def load_k8s_flavor(self):
        # fills K8SNodeFlavor
        values = dict()
        for key, val in self._workload_sizes["kubernetes"].items():
            values[key.upper()] = val["value"]
        self._k8s_node_flavor = Enum("K8SNodeFlavor", values)

    def load_k8s_sizes(self):
        # fills K8S_SIZES
        self._k8s_sizes = dict()
        for key, val in self._workload_sizes["kubernetes"].items():
            self.K8S_SIZES[self.K8SNodeFlavor[key.upper()]] = {"cru": val["cru"], "mru": val["mru"], "sru": val["sru"]}

    def load_s3_zdb_size(self):
        # fills S3ZDBSize
        values = dict()
        for key, val in self._workload_sizes["zdb"].items():
            values[key.upper()] = val["value"]
        self._s3_zdb_size = Enum("S3ZDBSize", values)

    def load_s3_zdb_size_details(self):
        # fills S3_ZDB_SIZES
        self._s3_zdb_sizes = dict()
        for key, val in self._workload_sizes["zdb"].items():
            self.S3_ZDB_SIZES[self.S3ZDBSize[key.upper()]] = {"sru": val["sru"]}

    def load_vdc_flavors(self):
        # fills VDCFlavor
        values = dict()
        for key in self._plans_data:
            values[key.upper()] = key
        self._vdc_flavor = Enum("VDCFlavor", values)

    def load_vdc_plans(self):
        # fills VDC_FLAVORS
        self._vdc_flavors = dict()
        for key, val in self._plans_data.items():
            self.VDC_FLAVORS[self.VDCFlavor[key.upper()]] = {
                "k8s": {
                    "no_nodes": val["k8s"]["no_nodes"],
                    "size": self.K8SNodeFlavor[val["k8s"]["size"].upper()],
                    "controller_size": self.K8SNodeFlavor[val["k8s"]["controller_size"].upper()],
                },
                "s3": {"size": self.S3ZDBSize[val["s3"]["size"].upper()], "upto": val["s3"]["upto"]},
                "duration": val["duration"],
            }

    def load_services(self):
        values = {}
        for service in self._prices_data["services"]:
            values[service.upper()] = service
        self._services = Enum("Services", values)

    def load_prices(self):
        self._prices = {"plans": {}, "nodes": {}, "services": {}}
        for plan, cost in self._prices_data["plans"].items():
            self._prices["plans"][self.VDCFlavor[plan.upper()]] = cost

        for node, cost in self._prices_data["nodes"].items():
            self._prices["nodes"][self.K8SNodeFlavor[node.upper()]] = cost

        for service, cost in self._prices_data["services"].items():
            self._prices["services"][self.Services[service.upper()]] = cost


VDC_SIZE = VDCSize()
