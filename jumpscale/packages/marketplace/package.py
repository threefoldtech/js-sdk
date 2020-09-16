from jumpscale.loader import j


class marketplace:
    def install(self, **kwargs):
        """Called when package is added
        """
        # http_location = j.sals.nginx.main.websites.default_80.locations.get(name="marketplace_root_proxy")
        # http_location.port = "80"
        # http_location.scheme = "http"
        # https_location = j.sals.nginx.main.websites.default_443.locations.get(name="marketplace_root_proxy")
        # https_location.port = "443"
        # https_location.scheme = "https"
        # for location in [http_location, https_location]:
        #     location.location_type = "proxy"
        #     location.path_url = "/"
        #     location.path_dest = "/marketplace"
        #     location.save()

        location_actors_443 = j.sals.nginx.main.websites.default_443.locations.get(name="marketplace_actors")
        location_actors_443.is_auth = False
        location_actors_443.is_admin = False
        location_actors_443.save()

        location_actors_80 = j.sals.nginx.main.websites.default_80.locations.get(name="marketplace_actors")
        location_actors_80.is_auth = False
        location_actors_80.is_admin = False
        location_actors_80.save()

        j.sals.nginx.main.websites.default_443.configure()
        j.sals.nginx.main.websites.default_80.configure()
        WALLET_NAME = j.sals.marketplace.deployer.WALLET_NAME
        if WALLET_NAME not in j.clients.stellar.list_all():
            secret = kwargs.get("secret", None)
            wallet = j.clients.stellar.new(WALLET_NAME, secret=secret, network="TEST")
            if not secret:
                wallet.activate_through_friendbot()
                wallet.add_known_trustline("TFT")
            wallet.save()

    def uninstall(self):
        """Called when package is deleted
        """
        j.sals.nginx.main.websites.default_443.locations.delete("marketplace_root_proxy")
        j.sals.nginx.main.websites.default_80.locations.delete("marketplace_root_proxy")
