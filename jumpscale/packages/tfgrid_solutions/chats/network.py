from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployer, deployment_context, solutions


class NetworkDeploy(GedisChatBot):
    steps = ["welcome", "start", "ip_config", "network_reservation", "network_info"]
    title = "Network"

    @chatflow_step(title="Welcome")
    def welcome(self):
        self.md_show_update("Initializing chatflow...")
        deployer.chatflow_pools_check()
        if solutions.list_network_solutions():
            self.action = self.single_choice(
                "Would you like to create a new network, or add access to an existing one?",
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
                self.solution_name = deployer.ask_name(
                    self, "Please enter a name for your workload (Needed to track your solution on the grid)"
                )
                network_solutions = solutions.list_network_solutions(sync=False)
                valid = True
                for sol in network_solutions:
                    if sol["Name"] == self.solution_name:
                        valid = False
                        self.md_show("The specified solution name already exists. please choose another name.")
                        break
                    valid = True
        elif self.action == "Add Access":
            self.network_view = deployer.select_network(self)

    @chatflow_step(title="IP Configuration")
    def ip_config(self):
        ips = ["IPv6", "IPv4"]
        self.ipversion = self.single_choice(
            "How would you like to connect to your network? If unsure, choose IPv4", ips, required=True, default="IPv4",
        )
        self.md_show_update("Searching for access node...")
        pools = [
            p
            for p in j.sals.zos.pools.list()
            if p.node_ids and p.cus >= 0 and p.sus >= 0 and p.empty_at > j.data.time.now().timestamp
        ]
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

    @chatflow_step(title="Reservation")
    @deployment_context()
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
                success = deployer.wait_workload(wid, self, breaking_node_id=self.access_node.node_id)
            except StopChatFlow as e:
                if self.action == "Create":
                    solutions.cancel_solution(self.config["ids"])
                raise e
            if not success:
                raise DeploymentFailed(f"Failed to deploy workload {wid}", wid=wid)

    @chatflow_step(title="Network Information", disable_previous=True, final_step=True)
    def network_info(self):
        self.filename = "wg-{}.conf".format(self.config["rid"])
        self.wgconf = self.config["wg"]

        msg = f"""\
        <h3> Use the following template to configure your wireguard connection. This will give you access to your network. </h3>
        <h3> Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed </h3>
        <br />
        <p style="text-align:center">{self.wgconf.replace(chr(10), "<br />")}</p>
        <br />
        <h3>In order to have the network active and accessible from your local/container machine, navigate to where the config is downloaded and start your connection using `wg-quick up &lt;your_download_dir&gt;/{self.filename}`</h3>
        """
        self.download_file(msg=dedent(msg), data=self.wgconf, filename=self.filename, html=True)


chat = NetworkDeploy
