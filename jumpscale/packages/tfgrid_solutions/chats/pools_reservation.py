import requests

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.packages.tfgrid_solutions.models import PoolConfig
from jumpscale.core.base import StoredFactory
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
            self.action = self.single_choice(
                "Do you want to create a new pool or extend one?", ["create", "extend"], required=True, default="create"
            )

    @chatflow_step(title="Pool Capacity")
    def reserve_pool(self):
        if self.action == "create":
            self.pool_data = deployer.create_pool(self)
        else:
            pool_id = deployer.select_pool(self)
            self.pool_data = deployer.extend_pool(self, pool_id)

    @chatflow_step(title="Pool Info")
    def pool_success(self):
        if self.action == "create":
            pool_id = self.pool_data.reservation_id
            self.md_show(
                f"Transaction successful. it may take a few minutes to reflect. please click next to add a local name for your pool {pool_id}"
            )
            valid = False
            pool_factory = StoredFactory(PoolConfig)
            while not valid:
                pool_name = self.string_ask("Please choose a name to identify your pool locally", required=True)
                _, _, result = pool_factory.find_many(name=pool_name)
                if list(result):
                    self.md_show("the name is already used. please choose a different one")
                else:
                    p = pool_factory.new(f"pool_{pool_id}")
                    p.name = pool_name
                    p.pool_id = pool_id
                    p.save()
                    valid = True
        else:
            self.md_show("Transaction successful. it may take a few minutes to reflect.")


chat = PoolReservation
