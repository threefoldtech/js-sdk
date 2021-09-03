import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.packages.tfgrid_solutions.models import PoolConfig
from jumpscale.core.base import StoredFactory
from jumpscale.sals.reservation_chatflow import deployer


class PoolExtend(GedisChatBot):
    steps = ["pool_start", "reserve_pool", "pool_success"]
    title = "Capacity Pool Extend"

    @chatflow_step(title="Welcome")
    def pool_start(self):
        self.md_show_update("It will take a few seconds to be ready to help you ...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")

        self.pool_id = self.kwargs["pool_id"]

    @chatflow_step(title="Capacity Pool")
    def reserve_pool(self):
        self.pool_data = deployer.extend_pool(self, self.pool_id)

    @chatflow_step(title="Capacity Pool Info", final_step=True)
    def pool_success(self):

        self.md_show(
            f"Transaction Succeeded! You just extended your capacity pool. It may take few minutes to reflect."
        )


chat = PoolExtend
