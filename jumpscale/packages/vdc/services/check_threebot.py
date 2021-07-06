import gevent
from jumpscale.loader import j

from jumpscale.clients.explorer.models import WorkloadType
from jumpscale.sals.vdc.models import KubernetesRole
from jumpscale.sals.zos import get as get_zos
from jumpscale.tools.vdc.reporting import _filter_vdc_workloads
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class CheckThreebot(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        """Check that Threebot Container is UP and Redeploy if DOWN
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        zos = get_zos()
        threebot_workload_types = [WorkloadType.Container, WorkloadType.Subdomain]
        j.logger.info("Check VDC threebot service: Check if Threebot containers in all VDCs is UP")
        for vdc_name in j.sals.vdc.list_all():
            vdc_instance = j.sals.vdc.find(vdc_name)

            # Check if vdc is empty
            if vdc_instance.is_empty():
                j.logger.warning(f"Check VDC threebot service: {vdc_name} is empty")
                gevent.sleep(0.1)
                continue

            vdc_instance.load_info()

            # Check if vdc has not minmal Components
            if (not vdc_instance.kubernetes) or vdc_instance.expiration < j.data.time.now().timestamp:
                j.logger.warning(f"Check VDC threebot service: {vdc_name} is expired or not found")
                gevent.sleep(0.1)
                continue

            master_node = [n for n in vdc_instance.kubernetes if n.role == KubernetesRole.MASTER]
            if not master_node:
                j.logger.warning(f"Check VDC threebot service: {vdc_name} master not deployed")
                gevent.sleep(0.1)
                continue

            master_ip = master_node[-1].public_ip
            # Check if vdc master is not reachable
            if not j.sals.nettools.tcp_connection_test(master_ip, 6443, 10):
                j.logger.warning(
                    f"Check VDC threebot service: {vdc_name} master node is not reachable on public ip: {master_ip}"
                )
                gevent.sleep(0.1)
                continue

            vdc_indentity = "vdc_ident_" + vdc_instance.solution_uuid
            zos = get_zos(identity_name=vdc_indentity)

            # Check if threebot domain is not reachable
            if not j.sals.nettools.wait_http_test(f"https://{vdc_instance.threebot.domain}", timeout=10):
                j.logger.warning(f"Check VDC threebot service: {vdc_name} threebot is DOWN")
                # List All workloads related to threebot
                workloads = [
                    workload
                    for workload in _filter_vdc_workloads(vdc_instance)
                    if workload.info.workload_type in threebot_workload_types
                ]
                decomission_status = True
                pool_id = 0
                # Decomission All the workloads related to threebot
                for workload in workloads:
                    # Check that container is threebot not any other thing
                    if workload.info.workload_type == WorkloadType.Container:
                        if "SDK_VERSION" in workload.environment.keys():
                            zdb_farms = workload.environment.get("S3_AUTO_TOPUP_FARMS")
                            pool_id = workload.info.pool_id
                        else:
                            gevent.sleep(0.1)
                            continue

                    zos.workloads.decomission(workload.id)
                    # Check if workload decomission failed
                    if not j.sals.reservation_chatflow.deployer.wait_workload_deletion(
                        workload.id, identity_name=vdc_indentity
                    ):
                        decomission_status = False
                        j.logger.error(f"Check VDC threebot service: Failed to decomission {workload.id}")
                        break

                if decomission_status:
                    # Deploy a new threebot container
                    deployer = vdc_instance.get_deployer()

                    try:
                        kubeconfig = deployer.kubernetes.download_kube_config(master_ip)
                    except Exception as e:
                        j.logger.error(
                            f"Check VDC threebot service: Failed to download kubeconfig for vdc {vdc_name} with error {e}"
                        )
                        gevent.sleep(0.1)
                        continue

                    minio_wid = 0
                    try:
                        threebot_wid = deployer.threebot.deploy_threebot(
                            minio_wid, pool_id, kubeconfig, zdb_farms=zdb_farms
                        )
                        j.logger.info(f"Check VDC threebot service: {vdc_name} threebot new wid: {threebot_wid}")
                    except Exception as e:
                        j.logger.error(
                            f"Check VDC threebot service: Can't deploy threebot for {vdc_name} with error{e}"
                        )
            else:
                j.logger.info(f"Check VDC threebot service: {vdc_name} threebot is UP")

            gevent.sleep(0.1)


service = CheckThreebot()
