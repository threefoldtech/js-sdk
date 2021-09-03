from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j
from jumpscale.sals.vdc.s3_auto_topup import (
    check_s3_utilization,
    get_zdb_farms_distribution,
    get_farm_pool_id,
    extend_zdbs,
    get_target_s3_zdb_config,
    MINIO_CONFIG_DICT,
)
from jumpscale.sals.reservation_chatflow import solutions
from jumpscale.sals.zos import get as get_zos
import math
import uuid
from jumpscale.tools import http


"""
S3_AUTO_TOP_SOLUTIONS: dict {
    "farm_names": []
    "extension_size": 10,
    "max_storage": 3, * 1024 # default
    "threshold": 0.7,
    "clear_threshold": 0.4,
    "targets": {
        "solution_name": {
            "minio_api_url": "myminio.com:9000",
            "healing_url": "myminio.com:9010"
            "max_storage": 10 * 1024 # override,
        }
    }
}
"""


class S3AutoTopUp(BackgroundService):
    def __init__(self, interval=60 * 60 * 2, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        """
        1- check_s3_utilization
        2- get solution_uuid of the solution
        3- get_zdb_farms_distribution
        4- get_farm_pool_id for the returned farm names
        5- extend_zdbs
        6- get new config
        """
        return  # disabled as there is no longer s3 (minio) part of the vdc TODO: remove when new zdb topup is running
        for sol_config in self.list_auto_top_up_config():
            _, required_cap = check_s3_utilization(
                sol_config["minio_api_url"],
                sol_config["threshold"],
                sol_config["clear_threshold"],
                sol_config["max_storage"],
            )

            if not required_cap:
                continue

            no_zdbs = math.floor(required_cap / sol_config["extension_size"])
            farm_names = get_zdb_farms_distribution(sol_config["solution_uuid"], sol_config["farm_names"], no_zdbs)
            pool_ids = []
            farm_pools = {}
            for farm_name in farm_names:
                pool_id = farm_pools.get(farm_name)
                if not pool_id:
                    pool_id = get_farm_pool_id(farm_name)
                    farm_pools[farm_name] = pool_id
                pool_ids.append(pool_id)

            wids, _ = extend_zdbs(
                sol_config["name"],
                pool_ids,
                sol_config["solution_uuid"],
                uuid.uuid4().hex,
                sol_config["duration"],
                sol_config["extension_size"],
            )
            if len(wids) != no_zdbs:
                j.logger.error(f"AUTO_TOPUP: couldn't deploy all required zdbs. successful workloads {wids}")

            zdb_configs = get_target_s3_zdb_config(sol_config["name"])
            config_dict = MINIO_CONFIG_DICT.copy()
            config_dict["datastor"]["shards"] = zdb_configs
            config_dict["datastor"]["pipeline"]["distribution"] = {"data_shards": 6, "parity_shards": 4}
            try:
                res = http.post(
                    f"{sol_config['healing_url']}/config",
                    j.data.serializers.json.dumps(config_dict),
                    headers={"Content-Type": "application/json"},
                )
                res.raise_for_status()
            except Exception as e:
                j.logger.error(
                    f"AUTO_TOPUP: couldn't update minio config for solution {sol_config['name']} due to error: {str(e)}"
                )
                j.tools.alerthandler.alert_raise(
                    app_name="s3_auto_topup",
                    category="internal_errors",
                    message=f"AUTO_TOPUP: couldn't update minio config for solution {sol_config['name']} due to error: {str(e)}",
                    alert_type="exception",
                )

    @staticmethod
    def list_auto_top_up_config():
        config = j.core.config.set_default(
            "S3_AUTO_TOP_SOLUTIONS", {"max_storage": 3 * 1024, "threshold": 0.7, "clear_threshold": 0.4, "targets": {}}
        )
        if not isinstance(config, dict):
            j.logger.error("AUTO_TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!")
            j.tools.alerthandler.alert_raise(
                app_name="s3_auto_topup",
                category="validation",
                message="AUTO_TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!",
                alert_type="exception",
            )
            return
        default_extension_size = config.get("extension_size", 10)
        default_max_storage = config.get("max_storage")
        default_threshold = config.get("threshold")
        default_clear_threshold = config.get("clear_threshold")
        default_farm_names = config.get("farm_names")
        defaults = [default_max_storage, default_threshold, default_clear_threshold, default_farm_names]
        if not all(defaults):
            j.logger.error("AUTO_TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!")
            j.tools.alerthandler.alert_raise(
                app_name="s3_auto_topup",
                category="validation",
                message="AUTO_TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!",
                alert_type="exception",
            )
            return

        targets = config.get("targets", {})
        if not isinstance(targets, dict):
            j.logger.error("AUTO_TOPUP: S3_AUTO_TOP_SOLUTIONS targets config is not valid!")
            j.tools.alerthandler.alert_raise(
                app_name="s3_auto_topup",
                category="validation",
                message="AUTO_TOPUP: S3_AUTO_TOP_SOLUTIONS targets config is not valid!",
                alert_type="exception",
            )
            return

        zos = get_zos()
        minio_solutions = {sol["Name"]: sol for sol in solutions.list_minio_solutions()}

        for sol_name, sol_config in targets.items():
            if sol_name not in minio_solutions:
                j.logger.warning(f"AUTO_TOPUP: solution {sol_name} is not a current s3 solution")
                continue
            minio_solution = minio_solutions[sol_name]
            minio_pool = zos.pools.get(minio_solution["Primary Pool"])
            duration = minio_pool.empty_at - j.data.time.utcnow().timestamp
            workload = zos.workloads.get(minio_solution["wids"][0])
            solution_uuid = solutions.get_solution_uuid(workload)
            if not isinstance(sol_config, dict) or not all(
                [key in sol_config for key in ["minio_api_url", "healing_url"]]
            ):
                j.logger.error(f"AUTO_TOPUP: target {sol_name} config is not valid!")
                j.tools.alerthandler.alert_raise(
                    app_name="s3_auto_topup",
                    category="validation",
                    message=f"AUTO_TOPUP: target {sol_name} config is not valid!",
                    alert_type="exception",
                )
                continue

            yield {
                "name": sol_name,
                "solution_uuid": solution_uuid,
                "extension_size": sol_config.get("extension_size", default_extension_size),
                "minio_api_url": sol_config["minio_api_url"],
                "healing_url": sol_config["healing_url"],
                "max_storage": sol_config.get("max_storage", default_max_storage),
                "threshold": sol_config.get("threshold", default_threshold),
                "clear_threshold": sol_config.get("clear_threshold", default_clear_threshold),
                "duration": duration,
                "farm_names": sol_config.get("farm_names", default_farm_names),
            }


service = S3AutoTopUp()
