from jumpscale.loader import j


class marketplacevdc:
    def uninstall(self):
        """Called when package is deleted
        """
        j.sals.nginx.main.websites.default_443.locations.delete("marketplacevdc_root_proxy")
        j.sals.nginx.main.websites.default_80.locations.delete("marketplacevdc_root_proxy")
