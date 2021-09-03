from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j


class ZDBAutoTopUp(BackgroundService):
    def __init__(self, interval=60 * 60 * 2, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        config = j.core.config.set_default(
            "S3_AUTO_TOP_SOLUTIONS", {"max_storage": None, "threshold": 0.7, "clear_threshold": 0.4}
        )
        for instance_name in j.sals.vdc.list_all():
            vdc = j.sals.vdc.find(instance_name)
            vdc.load_info()
            monitor = vdc.get_zdb_monitor()

            required_cap = monitor.get_extension_capacity(
                config["threshold"], config["clear_threshold"], config["max_storage"]
            )
            monitor.extend(required_cap, config.get("farm_names"), config.get("extension_size", 10))


service = ZDBAutoTopUp()
