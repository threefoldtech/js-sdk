from jumpscale.loader import j
class marketplace:
    def install(self, **kwargs):
        """
        kwargs: take only wallet secret it will be used to create `demos_wallet` if doesn't exist.
        """
        if "demos_wallet" not in j.clients.stellar.list_all():
            secret = kwargs.get("secret", None)
            wallet = j.clients.stellar.new("demos_wallet", secret=secret, network="TEST")
            if not secret:
                wallet.activate_through_friendbot()
                wallet.add_known_trustline("TFT")
            wallet.save()