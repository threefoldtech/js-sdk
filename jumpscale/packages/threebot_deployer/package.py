from jumpscale.loader import j


class threebot_deployer:
    def install(self):
        location_actors_443 = j.sals.nginx.main.websites.default_443.locations.get(name="threebot_deployer_actors")
        location_actors_443.is_auth = False
        location_actors_443.is_admin = False
        location_actors_443.save()

        location_actors_80 = j.sals.nginx.main.websites.default_80.locations.get(name="threebot_deployer_actors")
        location_actors_80.is_auth = False
        location_actors_80.is_admin = False
        location_actors_80.save()

        j.sals.nginx.main.websites.default_443.configure()
        j.sals.nginx.main.websites.default_80.configure()

    def start(self):
        self.install()

    def uninstall(self):
        """Called when package is deleted
        """
        j.sals.nginx.main.websites.default_443.locations.delete("threebot_deployer_root_proxy")
        j.sals.nginx.main.websites.default_80.locations.delete("threebot_deployer_root_proxy")
