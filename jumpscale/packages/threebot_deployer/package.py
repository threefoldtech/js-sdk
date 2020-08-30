from jumpscale.loader import j


class threebot_deployer:
    def uninstall(self):
        """Called when package is deleted
        """
        j.sals.nginx.main.websites.default_443.locations.delete("threebot_deployer_root_proxy")
        j.sals.nginx.main.websites.default_80.locations.delete("threebot_deployer_root_proxy")
