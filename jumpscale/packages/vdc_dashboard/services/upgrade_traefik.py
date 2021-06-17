from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class UpgradeTraefik(BackgroundService):
    def __init__(self, interval=5 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.info("Starting upgrade traefik service")
        current_ver = self.get_traefik_version()
        upgrade_to_ver = j.core.db.get("traefik:version:latest")
        if not upgrade_to_ver:
            upgrade_to_ver = "2.4.8"
            j.core.db.set("traefik:version:latest", upgrade_to_ver)
        else:
            upgrade_to_ver = upgrade_to_ver.decode("utf-8")

        if current_ver != upgrade_to_ver:
            j.logger.info(f"Upgrade Traefik Service:: Updating traefik from {current_ver} to {upgrade_to_ver}")
            vdc_instance = j.sals.vdc.find(list(j.sals.vdc.list_all())[0], load_info=True)
            vdc_instance.get_deployer().kubernetes.upgrade_traefik(version=upgrade_to_ver)
        else:
            j.logger.info(f"Upgrade Traefik Service:: Traefik using latest version {current_ver}")

    def get_traefik_version(self):
        current_ver = j.core.db.get("traefik:version:current")
        if not current_ver:
            _, out, _ = j.sals.kubernetes.Manager()._execute("helm list -A -o json")
            results = j.data.serializers.json.loads(out)
            for release in results:
                if release["name"] == "traefik":
                    current_ver = release["app_version"]
                    j.core.db.set("traefik:version:current", current_ver)
                else:
                    continue
        else:
            current_ver = current_ver.decode("utf-8")

        return current_ver


service = UpgradeTraefik()
