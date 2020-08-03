import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer


class PoolReservation(GedisChatBot):
    steps = ["pool_start", "reserve_pool", "pool_success"]
    title = "Pool"

    @chatflow_step(title="Welcome")
    def pool_start(self):
        self.pools = j.sals.zos.pools.list()
        if not self.pools:
            self.action = "create"
        else:
            self.action = self.single_choice("Do you want to create a new pool or extend one?", ["create", "extend"])

    @chatflow_step(title="Pool Capacity")
    def reserve_pool(self):
        if self.action == "create":
            self.pool_data = deployer.create_pool(self)
        else:
            pool_id = deployer.select_pool(self)
            self.pool_data = deployer.extend_pool(self, pool_id)

    @chatflow_step(title="Pool Info")
    def pool_success(self):
        self.md_show(f"Transaction successful. it may take a few minutes to reflect")


chat = PoolReservation
