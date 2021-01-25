from textwrap import dedent
import random
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployer, deployment_context, solutions
from collections import defaultdict


class NetworkBase(GedisChatBot):
    steps = ["start", "ip_config", "access_node_selection", "network_reservation", "network_info"]

    def _init(self):
        self.md_show_update("Initializing chatflow...")
        deployer.chatflow_pools_check()
        self.solution_metadata = {}

    @chatflow_step(title="Network Name")
    def start(self):
        self._init()

    @chatflow_step(title="IP Configuration")
    def ip_config(self):
        ips = ["IPv6", "IPv4"]
        self.ipversion = self.single_choice(
            "How would you like to connect to your network? If unsure, choose IPv4", ips, required=True, default="IPv4",
        )

    @chatflow_step(title="Access Node Selection")
    def access_node_selection(self):
        self.md_show_update("Fetching Access Nodes...")
        pools = [
            p
            for p in j.sals.zos.get().pools.list()
            if p.node_ids and p.cus >= 0 and p.sus >= 0 and p.empty_at > j.data.time.now().timestamp
        ]

        access_nodes_pools = defaultdict(list)
        for p in pools:
            for node_id in p.node_ids:
                access_nodes_pools[node_id].append(p.pool_id)
        available_access_nodes = {}
        all_access_nodes = filter(
            lambda node: node.node_id in access_nodes_pools, j.sals.zos.get()._explorer.nodes.list()
        )
        if self.ipversion == "IPv4":
            ip_filter = j.sals.zos.get().nodes_finder.filter_public_ip4
        else:
            ip_filter = j.sals.zos.get().nodes_finder.filter_public_ip6
        available_access_nodes = {
            n.node_id: n for n in all_access_nodes if ip_filter(n) and j.sals.zos.get().nodes_finder.filter_is_up(n)
        }

        if not available_access_nodes:
            raise StopChatFlow("There are no available access nodes in your existing pools")

        access_node_id = self.drop_down_choice(
            "Please select an access node or leave it empty to automatically select it",
            list(available_access_nodes.keys()),
        )
        if access_node_id:
            self.access_node = available_access_nodes[access_node_id]
            if len(access_nodes_pools[self.access_node.node_id]) > 1:
                self.pool = self.drop_down_choice(
                    "Please select a pool or leave it empty to automaically select it",
                    access_nodes_pools[self.access_node.node_id],
                )
                if not self.pool:
                    self.pool = random.choice(list(access_nodes_pools[self.access_node.node_id]))
            else:
                self.pool = access_nodes_pools[self.access_node.node_id][0]
        else:
            self.access_node = random.choice(list(available_access_nodes.values()))
            self.pool = random.choice(list(access_nodes_pools[self.access_node.node_id]))

    @chatflow_step(title="Reservation")
    @deployment_context()
    def network_reservation(self):
        # create config first
        for wid in self.config["ids"]:
            try:
                success = deployer.wait_workload(wid, self, breaking_node_id=self.access_node.node_id)
            except StopChatFlow as e:
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
