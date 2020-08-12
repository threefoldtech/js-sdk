from jumpscale.packages.tfgrid_solutions.chats.mattermost import MattermostDeploy as BaseMattermostDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class MattermostDeploy(BaseMattermostDeploy, MarketPlaceChatflow):
    @chatflow_step()
    def mattermost_start(self):
        self._validate_user()
        super().mattermost_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def mattermost_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            mattermost_solutions = solutions.list_mattermost_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in mattermost_solutions:
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
    def mattermost_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = MattermostDeploy
