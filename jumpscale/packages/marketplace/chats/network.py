from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.packages.tfgrid_solutions.chats.network_deploy import NetworkDeploy as BaseNetworkDeploy
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class NetworkDeploy(BaseNetworkDeploy, MarketPlaceChatflow):
    @chatflow_step(title="Welcome")
    def welcome(self):
        self._validate_user()
        if deployer.list_networks(self.user_info()["username"]):
            self.action = self.single_choice(
                "Do you want to create a new network or add access to an existing one?",
                options=["Create", "Add Access"],
            )
        else:
            self.action = "Create"
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Network Name")
    def start(self):
        if self.action == "Create":
            valid = False
            while not valid:
                self.solution_name = deployer.ask_name(self)
                network_solutions = solutions.list_network_solutions(self.user_info()["username"], sync=False)
                valid = True
                for sol in network_solutions:
                    if sol["Name"] == self.solution_name:
                        valid = False
                        self.md_show("The specified solution name already exists. please choose another.")
                        break
                    valid = True
            self.solution_name = f"{self.user_info()['username']}_{self.solution_name}"
        elif self.action == "Add Access":
            self.network_view = deployer.select_network(self.user_info()["username"], self)

    @chatflow_step(title="IP Configuration")
    def ip_config(self):
        ips = ["IPv6", "IPv4"]
        self.ipversion = self.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4", ips, required=True
        )

        pools = deployer.list_user_pools(self.user_info()["username"])
        farms = {deployer.get_pool_farm_id(p.pool_id): p.pool_id for p in pools}
        self.access_node = None
        for farm_id in farms:
            farm_name = deployer._explorer.farms.get(farm_id).name
            try:
                access_nodes = j.sals.reservation_chatflow.reservation_chatflow.get_nodes(
                    1, farm_names=[farm_name], ip_version=self.ipversion
                )
            except StopChatFlow:
                continue
            if access_nodes:
                self.access_node = access_nodes[0]
                self.pool = farms[farm_id]
                break
        if not self.access_node:
            raise StopChatFlow("There are no available access nodes in your existing pools")
        if self.action == "Create":
            self.ip_range = j.sals.reservation_chatflow.reservation_chatflow.get_ip_range(self)


chat = NetworkDeploy
