from jumpscale.loader import j


class marketplace:
    def install(self, **kwargs):
        """Called when package is added
        """
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
