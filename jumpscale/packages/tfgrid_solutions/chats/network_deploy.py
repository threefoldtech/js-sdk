import time

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer, solutions


class NetworkDeploy(GedisChatBot):
    steps = [
        "welcome",
        "start",
        "ip_config",
        "network_reservation",
        "network_info",
    ]
    title = "Network"

    @chatflow_step(title="Welcome")
    def welcome(self):
        if solutions.list_network_solutions():
            self.action = self.single_choice(
                "Do you want to create a new network or add access to an existing one?",
                options=["Create", "Add Access"],
                required=True,
                default="Create",
            )
        else:
            self.action = "Create"
        self.solution_metadata = {}

    @chatflow_step(title="Network Name")
    def start(self):
        if self.action == "Create":
            valid = False
            while not valid:
                self.solution_name = deployer.ask_name(self)
                network_solutions = solutions.list_network_solutions(sync=False)
                valid = True
                for sol in network_solutions:
                    if sol["Name"] == self.solution_name:
                        valid = False
                        self.md_show("The specified solution name already exists. please choose another.")
                        break
                    valid = True
        elif self.action == "Add Access":
            self.network_view = deployer.select_network(self)

    @chatflow_step(title="IP Configuration")
    def ip_config(self):
        ips = ["IPv6", "IPv4"]
        self.ipversion = self.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4", ips, required=True
        )
        self.md_show_update("searching for access node...")
        pools = j.sals.zos.pools.list()
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

    @chatflow_step(title="Reservation")
    def network_reservation(self):
        if self.action == "Create":
            try:
                self.config = deployer.deploy_network(
                    self.solution_name,
                    self.access_node,
                    self.ip_range,
                    self.ipversion,
                    self.pool,
                    **self.solution_metadata,
                )
            except Exception as e:
                raise StopChatFlow(f"Failed to register workload due to error {str(e)}")
        else:
            self.config = deployer.add_access(
                self.network_view.name,
                self.network_view,
                self.access_node.node_id,
                self.pool,
                self.ipversion == "IPv4",
                bot=self,
                **self.solution_metadata,
            )
        for wid in self.config["ids"]:
            try:
                success = deployer.wait_workload(wid, self)
            except StopChatFlow as e:
                if self.action == "Create":
                    solutions.cancel_solution(self.config["ids"])
                elif self.action == "Add Access":
                    for wid in self.config["ids"]:
                        j.sals.zos.workload.decomission(wid)
                raise e
            if not success:
                raise StopChatFlow(f"Failed to deploy workload {wid}")

    @chatflow_step(title="Network Information", disable_previous=True)
    def network_info(self):
        message = """
### Use the following template to configure your wireguard connection. This will give you access to your network.
#### Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed
Click next
to download your configuration
            """

        self.md_show(message, md=True, html=True)

        filename = "wg-{}.conf".format(self.config["rid"])
        self.download_file(msg=f'<pre>{self.config["wg"]}</pre>', data=self.config["wg"], filename=filename, html=True)

        message = f"""
### In order to have the network active and accessible from your local/container machine. To do this, execute this command:
\n<br />\n
#### ```wg-quick up /etc/wireguard/{filename}```
\n<br />\n
# Click next
            """

        self.md_show(message, md=True)


chat = NetworkDeploy
