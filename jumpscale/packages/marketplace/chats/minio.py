import math

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.chats.minio_deploy import MinioDeploy as BaseMinioDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class MinioDeploy(BaseMinioDeploy, MarketPlaceChatflow):
    @chatflow_step(title="Welcome")
    def deployment_start(self):
        self._validate_user()
        super().deployment_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def minio_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            minio_solutions = solutions.list_minio_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in minio_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    def zdb_nodes_selection(self):
        query = {"sru": 10}
        workload_name = "ZDB workloads"
        self.zdb_nodes, self.zdb_pool_ids = deployer.ask_multi_pool_distribution(
            self.solution_metadata["owner"], self, self.zdb_number, query, workload_name=workload_name
        )

    @chatflow_step(title="Minio Nodes")
    def minio_nodes_selection(self):
        queries = [
            {
                "sru": 10,
                "mru": math.ceil(self.minio_cont_resources["memory"] / 1024),
                "cru": self.minio_cont_resources["cpu"],
            }
        ] * self.minio_number
        workload_names = ["Primary"]
        if self.mode == "Master/Slave":
            workload_names.append("Secondary")
        self.minio_nodes, self.minio_pool_ids = deployer.ask_multi_pool_placement(
            self.solution_metadata["owner"], self, len(queries), queries, workload_names=workload_names,
        )

    @chatflow_step(title="Network")
    def minio_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = MinioDeploy
