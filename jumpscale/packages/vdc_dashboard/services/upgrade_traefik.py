from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService

UPGRADE_TO_VER = "9.20.1"


class UpgradeTraefik(BackgroundService):
    def __init__(self, interval=5 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)
        self.schedule_on_start = True

    def job(self):
        current_ver = self.get_traefik_version()
        if current_ver != UPGRADE_TO_VER:
            j.logger.info(f"Upgrade Traefik Service:: Updating traefik from {current_ver} to {UPGRADE_TO_VER}")
            vdc_instance = j.sals.vdc.find(list(j.sals.vdc.list_all())[0])
            vdc_instance.get_deployer().kubernetes.upgrade_traefik(version=UPGRADE_TO_VER)
        else:
            j.logger.info(f"Upgrade Traefik Service:: Traefik using latest version {current_ver}")

    def get_traefik_version(self):
        rc, out, err = j.sals.kubernetes.Manager()._execute("helm list -A -o json")
        if rc:
            raise j.exceptions.Timeout(f"Upgrade Traefik Service::{err}")

        results = j.data.serializers.json.loads(out)
        for release in results:
            if release["name"] == "traefik":
                return release["chart"].replace("traefik-", "")


service = UpgradeTraefik()
