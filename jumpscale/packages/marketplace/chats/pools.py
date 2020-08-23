from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer


class PoolReservation(MarketPlaceChatflow):
    steps = ["pool_start", "reserve_pool", "pool_success"]
    title = "Pool"

    @chatflow_step(title="Welcome")
    def pool_start(self):
        self._validate_user()
        self.pools = deployer.list_user_pools(self.user_info()["username"])
        if not self.pools:
            self.action = "create"
        else:
            self.action = self.single_choice(
                "Do you want to create a new pool or extend one?", ["create", "extend"], required=True, default="create"
            )

    @chatflow_step(title="Pool Capacity")
    def reserve_pool(self):
        if self.action == "create":
            self.pool_data = deployer.create_pool(self.user_info()["username"], self)
        else:
            pool_id = deployer.select_pool(self.user_info()["username"], self)
            self.pool_data = deployer.extend_pool(self, pool_id)

    @chatflow_step(title="Pool Info")
    def pool_success(self):
        self.md_show(f"Transaction successful. it may take a few minutes to reflect")


chat = PoolReservation
