from jumpscale.sals.marketplace import deployer, solutions, MarketPlaceChatflow
from jumpscale.packages.tfgrid_solutions.chats.threebot import ThreebotDeploy as BaseThreebotDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
import math


class ThreebotDeploy(BaseThreebotDeploy, MarketPlaceChatflow):
    @chatflow_step()
    def start(self):
        self._validate_user()
        super().start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def set_threebot_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            threebot_solutions = solutions.list_threebot_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in threebot_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self.solution_metadata["owner"], self, cu=cu, su=su, **query)
        self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Network")
    def threebot_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = ThreebotDeploy
