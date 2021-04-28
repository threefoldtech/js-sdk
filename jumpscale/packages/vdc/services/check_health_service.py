from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class HealthCheckService(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        self.zos = j.sals.zos.get()
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.debug("Health check service started.")
        for vdc_name in j.sals.vdc.list_all():
            vdc_instance = j.sals.vdc.find(vdc_name, load_info=True)
            if vdc_instance.has_minimal_components():
                # check ip units to be enough for a week
                pool_id = vdc_instance.kubernetes[0].pool_id

                ipv4us = self.zos.pools.get(pool_id).ipv4us
                if ipv4us < 604800:  # enough for a week
                    err_msg = f"Health check service: vdc: {vdc_name} public ip units is about to expire you have {ipv4us} which is enough for only a week"
                    j.logger.warning(err_msg)
                    j.tools.alerthandler.alert_raise(
                        app_name="health_check_service", category="kubernetes", message=err_msg, alert_type="vdc"
                    )
                    continue

                # check vdc kubernetes master public ip is reachable
                public_ip = vdc_instance.kubernetes[0].public_ip
                if not j.sals.nettools.tcp_connection_test(public_ip, 6443, 10):
                    err_msg = (
                        f"Health check service: vdc: {vdc_name} master node is not reachable on public ip: {public_ip}"
                    )
                    j.logger.critical(err_msg)
                    j.tools.alerthandler.alert_raise(
                        app_name="health_check_service", category="kubernetes", message=err_msg, alert_type="vdc"
                    )
                    continue

                # check threebot controller is reachable and up
                threebot_health_url = f"https://{vdc_instance.threebot.domain}/vdc_dashboard/api/controller/status"
                try:
                    j.tools.http.get(threebot_health_url).json()
                except Exception as e:
                    err_msg = f"Health check service: vdc: {vdc_name} threebot controller is not alive at: {threebot_health_url} due to: {str(e)}"
                    j.logger.critical(err_msg)
                    j.tools.alerthandler.alert_raise(
                        app_name="health_check_service", category="vdc_threebot", message=err_msg, alert_type="vdc"
                    )
                    continue

                j.logger.info(f"VDC: {vdc_name} is alive")
        j.logger.debug("Health check service ended.")


service = HealthCheckService()
