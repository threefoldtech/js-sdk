import math

from jumpscale.packages.tfgrid_solutions.chats.gollum import GollumDeploy as BaseGollumDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class GollumDeploy(BaseGollumDeploy, MarketPlaceChatflow):
    def _gollum_start(self):
        self._validate_user()
        super()._gollum_start()
        self.username = self.user_info()["username"]
        self.solution_metadata["owner"] = self.username

    @chatflow_step(title="Solution Name")
    def gollum_name(self):
        self._gollum_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            gollum_solutions = solutions.list_gollum_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in gollum_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
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
        cloud_units = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(
            self.solution_metadata["owner"], self, cu=cloud_units.cu, su=cloud_units.su, **query
        )

    @chatflow_step(title="Network")
    def gollum_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = GollumDeploy
