from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer


class PoolReservation(MarketPlaceChatflow):
    steps = ["pool_start", "reserve_pool", "pool_success"]
    title = "Capacity Pool"

    @chatflow_step(title="Welcome")
    def pool_start(self):
        self.username = self.user_info()["username"]
        self._validate_user()
        self.pools = deployer.list_user_pools(self.username)
        if not self.pools:
            self.action = "create"
        else:
            self.action = self.single_choice(
                "Do you want to create a new pool or extend one?", ["create", "extend"], required=True, default="create"
            )

    @chatflow_step(title="Capacity Pool")
    def reserve_pool(self):
        if self.action == "create":
            self.pool_data = deployer.create_pool(self.username, self)
        else:
            pool_id = deployer.select_pool(self.username, self)
            self.pool_data = deployer.extend_pool(self, pool_id)

    @chatflow_step(title="Pool Info")
    def pool_success(self):
        self.md_show(f"Transaction Succeeded! You just created a new capacity pool. It may take few minutes to reflect.")



chat = PoolReservation
