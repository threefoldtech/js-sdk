import math

from jumpscale.clients.explorer.models import Category, DiskType, ZDBMode
from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.chats.kubernetes_deploy import KubernetesDeploy as BaseKubernetesDeploy
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow.models import SolutionType


class KubernetesDeploy(BaseKubernetesDeploy, MarketPlaceChatflow):
    @chatflow_step()
    def deployment_start(self):
        self._validate_user()
        super().deployment_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def kubernetes_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            k8s_solutions = solutions.list_kubernetes_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in k8s_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    @chatflow_step(title="Containers' node id")
    def nodes_selection(self):
        queries = [self.master_query] * (self.workernodes.value + 1)
        workload_names = ["Master node"] + [f"Slave node {i+1}" for i in range(self.workernodes.value)]
        self.selected_nodes, self.selected_pool_ids = deployer.ask_multi_pool_placement(
            self.solution_metadata["owner"], self, len(queries), queries, workload_names=workload_names
        )

    @chatflow_step(title="Network")
    def network_selection(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = KubernetesDeploy
