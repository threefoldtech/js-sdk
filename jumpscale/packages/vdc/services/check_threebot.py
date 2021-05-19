import gevent
from jumpscale.loader import j

from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.sals.zos import get as get_zos
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.clients.explorer.models import WorkloadType


class CheckThreebot(BackgroundService):
    def __init__(self, interval=60, *args, **kwargs):
        """Check that Threebot Container is UP and Redeploy if DOWN
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        zos = get_zos()
        threebot_workload_types = [WorkloadType.Container, WorkloadType.Subdomain]
        j.logger.info("Check if Threebot containers in all VDCs is UP")
        for vdc_name in VDCFACTORY.list_all():
            vdc_instance = VDCFACTORY.find(vdc_name)
            zos = get_zos(identity_name=f"vdc_ident_{vdc_instance.solution_uuid}")
            if not j.sals.nettools.wait_http_test(f"https://{vdc_instance.threebot.domain}", timeout=10):
                j.logger.info(f"{vdc_instance.vdc_name} threebot is DOWN")
                workloads = zos.workloads.list_workloads(vdc_instance.identity_tid)
                j.logger.debug(f"Threebot Workloads:\n {workload}")
                for workload in workloads:
                    if workload.info.workload_type in threebot_workload_types:
                        zos.workloads.decomission(workload.id)
                        wid = zos.workloads.deploy(workload)
                        j.logger.debug(f"{workload.info.workload_type} new id is {wid}")
                j.logger.info(f"{vdc_instance.vdc_name} threebot redeployed")
            else:
                j.logger.debug(f"{vdc_instance.vdc_name} threebot is UP")


service = CheckThreebot()
