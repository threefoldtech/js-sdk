from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j


class KubernetesAutoExtend(BackgroundService):
    def __init__(self, interval=60 * 5, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        for instance_name in j.sals.vdc.list_all():
            vdc = j.sals.vdc.find(instance_name)
            monitor = vdc.get_kubernetes_monitor()
            monitor.update_stats()
            if monitor.is_extend_triggered():
                j.logger.info(f"K8S_AUTO_EXTEND: extension triggered")
                wids = monitor.extend()
                if not wids:
                    j.logger.warning(f"K8S_AUTO_EXTEND: failed to extend k8s cluster.")


service = KubernetesAutoExtend()
