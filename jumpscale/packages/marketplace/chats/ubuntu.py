from jumpscale.loader import j
import math
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.packages.tfgrid_solutions.chats.ubuntu_deploy import UbuntuDeploy as BaseUbuntuDeploy
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class UbuntuDeploy(BaseUbuntuDeploy, MarketPlaceChatflow):
    steps = [
        "ubuntu_start",
        "ubuntu_name",
        "ubuntu_version",
        "container_resources",
        "select_pool",
        "ubuntu_network",
        "container_logs",
        "public_key_get",
        "container_node_id",
        "container_ip",
        "ipv6_config",
        "overview",
        "reservation",
        "ubuntu_access",
    ]

    @chatflow_step()
    def ubuntu_start(self):
        super().ubuntu_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def ubuntu_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            ubuntu_solutions = solutions.list_ubuntu_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in ubuntu_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.user_info()['username']}_{self.solution_name}"

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
