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
        zos = get_zos()
        for name in j.core.config.get("S3_AUTO_TOP_SOLUTIONS"):
            triggered_wids = check_s3_utilization(name)
            if not triggered_wids:
                return

            workload = zos.workloads.get(triggered_wids[0])
            solution_uuid = solutions.get_solution_uuid(workload)
            farms = get_zdb_farms_distribution(
                solution_uuid, j.core.config.get("S3_AUTO_TOPUP_FARMS"), len(triggered_wids)
            )
            pool_ids = []
            for farm in farms:
                pool_ids.append(get_farm_pool_id(farm))
            new_wids, password = extend_triggered_zdbs(name, triggered_wids, pool_ids, uuid.uuid4().hex)
            s3_configs = get_target_s3_zdb_config(name)
            # build the config and send it to minio


service = S3AutoTopUp()
