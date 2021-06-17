from jumpscale.loader import j
import gevent

UPGRADE_TO_VER = "2.4.8"


def get_traefik_version():
    _, out, _ = j.sals.kubernetes.Manager()._execute("helm list -A -o json")
    results = j.data.serializers.json.loads(out)
    for release in results:
        if release["name"] == "traefik":
            return release["app_version"]


j.logger.info("Starting upgrade traefik service")
current_ver = get_traefik_version()
while current_ver != UPGRADE_TO_VER:
    j.logger.info(f"Updating traefik from {current_ver} to {UPGRADE_TO_VER}")
    vdc_instance = j.sals.vdc.find(list(j.sals.vdc.list_all())[0], load_info=True)
    vdc_instance.get_deployer().kubernetes.upgrade_traefik(version=UPGRADE_TO_VER)
    current_ver = get_traefik_version()
    gevent.sleep(1)

j.logger.info(f"Traefik using latest version {current_ver}")
