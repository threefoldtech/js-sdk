from jumpscale.loader import j
class polls:
    def install(self, **kwargs):
        if "polls_receive" not in j.clients.stellar.list_all():
            secret = kwargs.get("secret", None)
            network = kwargs.get("network", "TEST")
            wallet = j.clients.stellar.new("polls_receive", secret=secret, network=network)
            if not secret:
                if network == "TEST":
                    wallet.activate_through_friendbot()
                else:
                    wallet.activate_through_threefold_service()
            wallet.save()