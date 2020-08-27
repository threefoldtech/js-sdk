from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.chats.network import NetworkDeploy as BaseNetworkDeploy
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class NetworkDeploy(BaseNetworkDeploy, MarketPlaceChatflow):
    @chatflow_step(title="Welcome")
    def welcome(self):
        self.username = self.user_info()["username"]
        self._validate_user()
        if deployer.list_networks(self.username):
            self.action = self.single_choice(
                "Do you want to create a new network or add access to an existing one?",
                options=["Create", "Add Access"],
                required=True,
                default="Create",
            )

        else:
            self.action = "Create"
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.username

    @chatflow_step(title="Network Name")
    def start(self):
        if self.action == "Create":
            valid = False
            while not valid:
                self.solution_name = deployer.ask_name(self)
                network_solutions = solutions.list_network_solutions(self.username, sync=False)
                valid = True
                for sol in network_solutions:
                    if sol["Name"] == self.solution_name:
                        valid = False
                        self.md_show("The specified solution name already exists. please choose another.")
                        break
                    valid = True
            self.solution_name = f"{self.username}_{self.solution_name}"
        elif self.action == "Add Access":
            self.network_view = deployer.select_network(self.username, self)

    @chatflow_step(title="IP Configuration")
    def ip_config(self):
        ips = ["IPv6", "IPv4"]
        self.ipversion = self.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4",
            ips,
            required=True,
            default="IPv4",
        )
        self.md_show_update("searching for access node...")
        pools = deployer.list_user_pools(self.username)
        self.access_node = None
        for pool in pools:
            try:
                access_nodes = j.sals.reservation_chatflow.reservation_chatflow.get_nodes(
                    1, ip_version=self.ipversion, pool_ids=[pool.pool_id]
                )
            except StopChatFlow:
                continue
            if access_nodes:
                self.access_node = access_nodes[0]
                self.pool = pool.pool_id
                break
        if not self.access_node:
            raise StopChatFlow("There are no available access nodes in your existing pools")
        if self.action == "Create":
            self.ip_range = j.sals.reservation_chatflow.reservation_chatflow.get_ip_range(self)


chat = NetworkDeploy
