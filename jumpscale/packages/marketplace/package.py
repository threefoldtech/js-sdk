from jumpscale.loader import j


class marketplace:
    def install(self, **kwargs):
        """Called when package is added
        """
        WALLET_NAME = j.sals.marketplace.deployer.WALLET_NAME
        if WALLET_NAME not in j.clients.stellar.list_all():
            secret = kwargs.get("secret", None)
            if not secret:
                j.logger.critical(f"Couldn't find wallet {WALLET_NAME} or its secret")
            else:
                wallet = j.clients.stellar.new(WALLET_NAME, secret=secret)
                wallet.save()
                j.logger.info(f"{WALLET_NAME} wallet has been imported successfully and ready to use.")

    def uninstall(self):
        """Called when package is deleted
        """
        j.sals.nginx.main.websites.default_443.locations.delete("marketplace_root_proxy")
        j.sals.nginx.main.websites.default_80.locations.delete("marketplace_root_proxy")
