from jumpscale.packages.tfgrid_solutions.chats.taiga_deploy import TaigaDeploy as BaseTaigaDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class TaigaDeploy(BaseTaigaDeploy, MarketPlaceChatflow):
    @chatflow_step()
    def taiga_start(self):
        self._validate_user()
        super().taiga_start()
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def taiga_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            monitoring_solutions = solutions.list_taiga_solutions(self.solution_metadata["owner"], sync=False)
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
    def taiga_network(self):
        self.network_view = deployer.select_network(self.solution_metadata["owner"], self)


chat = TaigaDeploy
