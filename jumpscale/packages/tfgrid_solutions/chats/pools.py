import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.packages.tfgrid_solutions.models import PoolConfig
from jumpscale.core.base import StoredFactory
from jumpscale.sals.reservation_chatflow import deployer


class PoolReservation(GedisChatBot):
    steps = ["pool_start", "reserve_pool", "pool_success"]
    title = "Capacity Pool"

    @chatflow_step(title="Welcome")
    def pool_start(self):
        self.md_show_update("It will take a few seconds to be ready to help you ...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")

    @chatflow_step(title="Capacity Pool")
    def reserve_pool(self):
        valid = False
        pool_factory = StoredFactory(PoolConfig)
        while not valid:
            self.pool_name = self.string_ask(
                "Please choose a name for your new capacity pool. This name will only be used by you to identify the pool for later usage and management.",
                required=True,
                is_identifier=True,
            )
            _, _, result = pool_factory.find_many(name=self.pool_name)
            if list(result):
                self.md_show("the name is already used. please choose a different one")
                continue
            valid = True
        self.pool_data = deployer.create_pool(self)

    @chatflow_step(title="Capacity Pool Info", final_step=True)
    def pool_success(self):
        pool_id = self.pool_data.reservation_id
        pool_factory = StoredFactory(PoolConfig)
        p = pool_factory.new(f"pool_{pool_id}")
        p.name = self.pool_name
        p.pool_id = pool_id
        p.save()
        self.md_show(
            f"Transaction Succeeded! You just created a new capacity pool. It may take few minutes to reflect."
        )


chat = PoolReservation
