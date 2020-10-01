from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, solutions


class ExtendThreebot(MarketPlaceAppsChatflow):

    title = "Extend 3Bot"
    steps = ["select_threebot", "new_expiration", "solution_extension", "success"]

    @chatflow_step(title="Select 3Bot")
    def select_threebot(self):
        self._validate_user()
        self.query = {"cru": 2, "mru": 2, "sru": 2.25}
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

    @chatflow_step(title="Success", final_step=True)
    def success(self):
        self.md_show("Your 3Bot has been extended successfully.")


chat = ExtendThreebot
