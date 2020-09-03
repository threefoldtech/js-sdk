from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace.chatflow import MarketPlaceChatflow
from jumpscale.sals.marketplace import deployer, solutions


class ExtendThreebot(MarketPlaceChatflow):

    title = "Extend 3Bot"
    steps = ["select_threebot", "new_expiration", "solution_extension", "success"]

    @chatflow_step(title="Select 3Bot")
    def select_threebot(self):
        self._validate_user()
        self.query = {"cru": 2, "mru": 2, "sru": 2}
        self.threebot_name = self.user_info()["username"]
        self.explorer = j.core.identity.me.explorer
        self.threebot_workloads = solutions.list_solutions(self.threebot_name, "threebot")
        self.threebot_names = [s["Name"] for s in self.threebot_workloads]
        self._threebots_dict = dict(zip(self.threebot_names, self.threebot_workloads))
        self.threebot_selected = self.single_choice(
            "Choose your 3Bot you want to extend?", self.threebot_names, required=True
        )
        self.pool_id = self._threebots_dict[self.threebot_selected]["Pool"]
        self.pool = j.sals.zos.pools.get(self.pool_id)

    @chatflow_step(title="New Expiration")
    def new_expiration(self):
        if self.pool.empty_at < 9223372036854775807:
            # Pool resources available
            min_timestamp_fromnow = self.pool.empty_at - j.data.time.get().timestamp
            default_time = self.pool.empty_at + 3900
        else:
            # Pool resources empty so empty_at value is max
            min_timestamp_fromnow = None
            default_time = j.data.time.get().timestamp + 15552000
        self.expiration = deployer.ask_expiration(self, default_time, min=min_timestamp_fromnow)

    @chatflow_step(title="Payment")
    def solution_extension(self):

        farm_id = deployer.get_pool_farm_id(self.pool_id)
        farm = deployer._explorer.farms.get(farm_id)
        assets = [w.asset for w in farm.wallet_addresses]
        if "FreeTFT" in assets:
            pool_nodes = j.sals.zos.nodes_finder.nodes_by_capacity(pool_id=self.pool_id)
            for node in pool_nodes:
                if not node.free_to_use:
                    assets.remove("FreeTFT")
                    break
        currency = self.single_choice("Please choose the currency", assets, required=True)
        self.currencies = [currency]
        self.pool_info, self.qr_code = deployer.extend_solution_pool(
            self, self.pool_id, self.expiration, self.currencies, **self.query
        )

        result = deployer.wait_pool_payment(
            self, self.pool_id, qr_code=self.qr_code, trigger_cus=self.pool.cus + 1, trigger_sus=self.pool.sus + 1
        )
        if not result:
            raise StopChatFlow(f"Waiting for pool payment timedout. pool_id: {self.pool_id}")

    @chatflow_step(title="Success", final_step=True)
    def success(self):
        self.md_show("Your 3Bot has been extended successfully")


chat = ExtendThreebot
