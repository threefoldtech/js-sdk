import math
import time
import uuid

from jumpscale.clients.explorer.models import Category, DiskType, ZDBMode
from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.chats.monitoring import MonitoringDeploy as BaseMonitoringDeploy
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow.models import SolutionType


class MonitoringDeploy(BaseMonitoringDeploy, MarketPlaceChatflow):
    @chatflow_step()
    def deployment_start(self):
        self._validate_user()
        super().deployment_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def choose_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            monitoring_solutions = solutions.list_monitoring_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in monitoring_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    @chatflow_step(title="Container's node ids")
    def container_node_ids(self):
        queries = []
        for name in self.tools_names:
            queries.append(
                {
                    "cru": self.query[name]["cpu"],
                    "mru": math.ceil(self.query[name]["memory"] / 1024),
                    "sru": math.ceil(self.query[name]["disk_size"] / 1024),
                }
            )
        self.selected_nodes, self.selected_pool_ids = deployer.ask_multi_pool_placement(
            self.solution_metadata["owner"], self, 3, queries, workload_names=self.tools_names
        )

    @chatflow_step(title="Network")
    def network_selection(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = MonitoringDeploy
