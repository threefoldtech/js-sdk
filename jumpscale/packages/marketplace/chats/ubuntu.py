import math

from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.chats.ubuntu import UbuntuDeploy as BaseUbuntuDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class UbuntuDeploy(BaseUbuntuDeploy, MarketPlaceChatflow):
    @chatflow_step()
    def _ubuntu_start(self):
        super()._ubuntu_start()
        self.username = self.user_info()["username"]
        self.solution_metadata["owner"] = self.username

    @chatflow_step(title="Solution name")
    def ubuntu_name(self):
        self._ubuntu_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            ubuntu_solutions = solutions.list_ubuntu_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in ubuntu_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True
        self.solution_name = f"{self.username}_{self.solution_name}"

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
    def ubuntu_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = UbuntuDeploy
