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
            "Choose the 3Bot you would like to extend", self.threebot_names, required=True
        )
        self.pool_id = self._threebots_dict[self.threebot_selected]["Pool"]
        self.pool = j.sals.zos.pools.get(self.pool_id)

    @chatflow_step(title="New Expiration")
    def new_expiration(self):
        DURATION_MAX = 9223372036854775807
        if self.pool.empty_at < DURATION_MAX:
            # Pool currently being consumed (compute or storage), default is current pool empty at + 65 mins
            min_timestamp_fromnow = self.pool.empty_at - j.data.time.get().timestamp
            default_time = self.pool.empty_at + 3900
        else:
            # Pool not being consumed (compute or storage), default is in 14 days (60*60*24*14 = 1209600)
            min_timestamp_fromnow = None
            default_time = j.data.time.get().timestamp + 1209600
        self.expiration = deployer.ask_expiration(self, default_time, min=min_timestamp_fromnow)

    @chatflow_step(title="Payment")
    def solution_extension(self):
        self.currencies = ["TFT"]
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
        self.md_show("Your 3Bot has been extended successfully.")


chat = ExtendThreebot
