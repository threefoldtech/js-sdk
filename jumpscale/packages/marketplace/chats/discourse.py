import math

from jumpscale.packages.tfgrid_solutions.chats.discourse import Discourse as BaseDiscourse
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class Discourse(BaseDiscourse, MarketPlaceChatflow):
    @chatflow_step()
    def discourse_start(self):
        self._validate_user()
        super().discourse_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def discourse_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            discourse_solutions = solutions.list_discourse_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in discourse_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self.solution_metadata["owner"], self, cu=cu, su=su, **query)

    @chatflow_step(title="Network")
    def discourse_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = Discourse
