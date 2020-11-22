from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j
from jumpscale.sals.vdc.auto_topup import (
    check_s3_utilization,
    get_zdb_farms_distribution,
    get_farm_pool_id,
    extend_triggered_zdbs,
    get_target_s3_zdb_config,
)
from jumpscale.sals.reservation_chatflow import solutions
from jumpscale.sals.zos import get as get_zos
import uuid


"""
S3_AUTO_TOP_SOLUTIONS: dict {
    "max_storage": 3, * 1024 # default
    "threshold": 0.7,
    "clear_threshold": 0.4,
    "targets": {
        "solution_name": {
            "healing_address": "https://myminio.com:9010",
            "max_storage": 10 * 1024 # override
        }
    }
}
"""


class S3AutoTopUp(BackgroundService):
    def __init__(self, name="s3_auto_topup", interval=60 * 60 * 2, *args, **kwargs):
        super().__init__(name, interval, *args, **kwargs)

    def job(self):
        """
        1- check_s3_utilization
        2- get solution_uuid of the solution
        3- get_zdb_farms_distribution
        4- get_farm_pool_id for the returned farm names
        5- extend_triggered_zdbs
        """
        pass

    def list_auto_top_up_config(self):
        config = j.core.config.set_default(
            "S3_AUTO_TOP_SOLUTIONS", {"max_storage": 3 * 1024, "threshold": 0.7, "clear_threshold": 0.4, "targets": {}}
        )
        if not isinstance(config, dict):
            j.logger.error("AUTO_ TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!")
            j.tools.alerthandler.alert_raise(
                appname="s3_auto_topup",
                category="validation",
                message="AUTO_ TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!",
                alert_type="exception",
            )
            return
        default_max_storage = config.get("defaul_max_storage")
        default_threshold = config.get("threshold")
        default_clear_threshold = config.get("clear_threshold")
        defaults = [default_max_storage, default_threshold, default_clear_threshold]
        if not all(defaults):
            j.logger.error("AUTO_ TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!")
            j.tools.alerthandler.alert_raise(
                appname="s3_auto_topup",
                category="validation",
                message="AUTO_ TOPUP: S3_AUTO_TOP_SOLUTIONS config is not valid!",
                alert_type="exception",
            )
            return

        targets = config.get("targets", {})
        if not isinstance(targets, dict):
            j.logger.error("AUTO_ TOPUP: S3_AUTO_TOP_SOLUTIONS targets config is not valid!")
            j.tools.alerthandler.alert_raise(
                appname="s3_auto_topup",
                category="validation",
                message="AUTO_ TOPUP: S3_AUTO_TOP_SOLUTIONS targets config is not valid!",
                alert_type="exception",
            )
            return

        zos = get_zos()
        minio_solutions = {sol["Name"]: sol for sol in solutions.list_minio_solutions()}

        for sol_name, sol_config in targets.items():
            if sol_name not in minio_solutions:
                j.logger.warning(f"AUTO_ TOPUP: solution {sol_name} is not a current s3 solution")
                continue
            minio_solution = minio_solutions[sol_name]
            workload = zos.workloads.get(minio_solution["wids"][0])
            solution_uuid = solutions.get_solution_uuid(workload)
            if not isinstance(sol_config, dict) or "healing_address" not in sol_config:
                j.logger.error(f"AUTO_ TOPUP: target {sol_name} config is not valid!")
                j.tools.alerthandler.alert_raise(
                    appname="s3_auto_topup",
                    category="validation",
                    message=f"AUTO_ TOPUP: target {sol_name} config is not valid!",
                    alert_type="exception",
                )

            yield {
                "name": sol_name,
                "solution_uuid": solution_uuid,
                "healing_address": sol_config["healing_address"],
                "max_storage": sol_config.get("max_storage", default_max_storage),
                "threshold": sol_config.get("threshold", default_threshold),
                "clear_threshold": sol_config.get("clear_threshold", default_clear_threshold),
            }


service = S3AutoTopUp()
