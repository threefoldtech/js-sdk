from jumpscale.packages.tfgrid_solutions.chats.gitea import GiteaDeploy as BaseGiteaDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class GiteaDeploy(BaseGiteaDeploy, MarketPlaceChatflow):
    def _gitea_start(self):
        self._validate_user()
        super()._gitea_start()
        self.username = self.user_info()["username"]
        self.solution_metadata["owner"] = self.username

    @chatflow_step(title="Solution name")
    def gitea_name(self):
        self._gitea_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            monitoring_solutions = solutions.list_gitea_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in monitoring_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    @chatflow_step(title="Pool")
    def select_pool(self):
        cu, su = deployer.calculate_capacity_units(**self.query)
        self.pool_id = deployer.select_pool(self.solution_metadata["owner"], self, cu=cu, su=su, **self.query)

    @chatflow_step(title="Network")
    def gitea_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = GiteaDeploy
