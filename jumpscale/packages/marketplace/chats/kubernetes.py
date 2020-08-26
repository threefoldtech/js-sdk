import math

from jumpscale.clients.explorer.models import Category, DiskType, ZDBMode
from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.chats.kubernetes import KubernetesDeploy as BaseKubernetesDeploy
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow.models import SolutionType


class KubernetesDeploy(BaseKubernetesDeploy, MarketPlaceChatflow):
    def _deployment_start(self):
        self._validate_user()
        super()._deployment_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def kubernetes_name(self):
        self._deployment_start()
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
        no_nodes = self.workernodes.value + 1
        workload_name = "Kubernetes nodes"
        self.selected_nodes, self.selected_pool_ids = deployer.ask_multi_pool_distribution(
            self.solution_metadata["owner"], self, no_nodes, self.master_query, workload_name=workload_name
        )

    @chatflow_step(title="Network")
    def network_selection(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = KubernetesDeploy
