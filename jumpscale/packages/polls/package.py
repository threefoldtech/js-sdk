from jumpscale.loader import j


class polls:
    def install(self, **kwargs):
        if "polls_receive" not in j.clients.stellar.list_all():
            secret = kwargs.get("secret", None)
            wallet = j.clients.stellar.new("polls_receive", secret=secret)
            if not secret:
                wallet.activate_through_threefold_service()
            wallet.save()
