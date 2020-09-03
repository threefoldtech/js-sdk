from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer


class PoolReservation(MarketPlaceChatflow):
    steps = ["pool_start", "reserve_pool", "pool_success"]
    title = "Capacity Pool"

    @chatflow_step(title="Welcome to Capacity Pool")
    def pool_start(self):
        self.username = self.user_info()["username"]
        self._validate_user()
        self.pools = deployer.list_user_pools(self.username)
        if not self.pools:
            self.action = "create"
        else:
            self.action = self.single_choice(
                "Would you like to create a new capacity pool, or extend an existing one?", ["Create", "Extend"], required=True, default="Create"
            )

    @chatflow_step(title="Capacity Pool")
    def reserve_pool(self):
        if self.action == "Create":
            self.pool_data = deployer.create_pool(self.username, self)
        else:
            pool_id = deployer.select_pool(self.username, self)
            self.pool_data = deployer.extend_pool(self, pool_id)

    @chatflow_step(title="Capacity Pool Information")
    def pool_success(self):
        self.md_show(f"Transaction Succeeded! You just created a new capacity pool. It may take few minutes to reflect.")



chat = PoolReservation
