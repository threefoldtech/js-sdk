from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService

UPGRADE_TO_VER = "2.4.8"


class UpgradeTraefik(BackgroundService):
    def __init__(self, interval=5 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        current_ver = self.get_traefik_version()
        if current_ver != UPGRADE_TO_VER:
            j.logger.info(f"Upgrade Traefik Service:: Updating traefik from {current_ver} to {UPGRADE_TO_VER}")
            vdc_instance = j.sals.vdc.find(list(j.sals.vdc.list_all())[0])
            vdc_instance.get_deployer().kubernetes.upgrade_traefik(version=UPGRADE_TO_VER)
        else:
            j.logger.info(f"Upgrade Traefik Service:: Traefik using latest version {current_ver}")

    def get_traefik_version(self):
        _, out, _ = j.sals.kubernetes.Manager()._execute("helm list -A -o json")
        results = j.data.serializers.json.loads(out)
        for release in results:
            if release["name"] == "traefik":
                return release["app_version"]


service = UpgradeTraefik()
