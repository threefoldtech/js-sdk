import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer


class FourToSixGateway(GedisChatBot):
    steps = []

    @j.baseclasses.chatflow_step()
    def pool_start(self):
        self.pools = j.sal.zosv2.pools.list()
        if not self.pools:
            self.action = "create"
        else:
            self.action = self.single_choice("Do you want to create a new pool or extend one?", ["create", "extend"])


chat = FourToSixGateway
