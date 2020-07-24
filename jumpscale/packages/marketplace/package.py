from jumpscale.loader import j
import os


class marketplace:
    def install(self):
        """Called when package is added
        """
        http_location = j.sals.nginx.main.websites.default_80.locations.get(name="marketplace_root_proxy")
        http_location.port = "80"
        http_location.scheme = "http"
        https_location = j.sals.nginx.main.websites.default_443.locations.get(name="marketplace_root_proxy")
        https_location.port = "443"
        https_location.scheme = "https"
        for location in [http_location, https_location]:
            location.location_type = "proxy"
            location.path_url = "/"
            location.path_dest = "/marketplace"
            location.save()
        j.sals.nginx.main.websites.default_443.configure()
        j.sals.nginx.main.websites.default_80.configure()

    def uninstall(self):
        """Called when package is deleted
        """
        j.sals.nginx.main.websites.default_443.locations.delete("marketplace_root_proxy")
        j.sals.nginx.main.websites.default_80.locations.delete("marketplace_root_proxy")
