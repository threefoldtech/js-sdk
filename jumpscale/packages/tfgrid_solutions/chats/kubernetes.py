import uuid
from textwrap import dedent

from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployer, deployment_context, solutions


class KubernetesDeploy(GedisChatBot):
    steps = [
        "kubernetes_name",
        "choose_flavor",
        "nodes_selection",
        "network_selection",
        "public_key_get",
        "ip_selection",
        "reservation",
        "success",
    ]
    title = "Kubernetes"

    def _deployment_start(self):
        deployer.chatflow_pools_check()
        deployer.chatflow_network_check(self)
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata = {}

    @chatflow_step(title="Solution Name")
    def kubernetes_name(self):
        self._deployment_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            k8s_solutions = solutions.list_kubernetes_solutions(sync=False)
            valid = True
            for sol in k8s_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True

    @chatflow_step(title="Master and Worker flavors")
    def choose_flavor(self):
        form = self.new_form()
        sizes = ["1 vCPU 2 GiB ram 50GiB disk space", "2 vCPUs 4 GiB ram 100GiB disk space"]
        cluster_size_string = form.drop_down_choice("Choose the size of your nodes", sizes, default=sizes[0])

        self.workernodes = form.int_ask(
            "Please specify the number of worker nodes", default=1, required=True, min=1
        )  # minimum should be 1

        form.ask()
        self.cluster_size = sizes.index(cluster_size_string.value) + 1
        if self.cluster_size == 1:
            self.master_query = self.worker_query = {"sru": 50, "mru": 2, "cru": 1}
        else:
            self.master_query = self.worker_query = {"sru": 100, "mru": 4, "cru": 2}

    @chatflow_step(title="Containers' node id")
    def nodes_selection(self):
        no_nodes = self.workernodes.value + 1
        workload_name = "Kubernetes nodes"
        self.selected_nodes, self.selected_pool_ids = deployer.ask_multi_pool_distribution(
            self, no_nodes, self.master_query, workload_name=workload_name
        )

    @chatflow_step(title="Network")
    def network_selection(self):
        self.network_view = deployer.select_network(self, self.all_network_viewes)

    @chatflow_step(title="Access keys and secret")
    def public_key_get(self):
        self.ssh_keys = self.upload_file(
            """Please upload your public SSH key to be able to access the depolyed container via ssh
                Note: please use keys compatible with Dropbear server eg: RSA""",
            required=True,
        ).split("\n")

        self.cluster_secret = self.string_ask("Please add the cluster secret", default="secret", required=True)

    @chatflow_step(title="IP selection")
    @deployment_context()
    def ip_selection(self):
        self.md_show_update("Deploying Network on Nodes....")
        # deploy network on nodes
        for i in range(len(self.selected_nodes)):
            node = self.selected_nodes[i]
            pool_id = self.selected_pool_ids[i]
            result = deployer.add_network_node(
                self.network_view.name,
                node,
                pool_id,
                self.network_view,
                bot=self,
                owner=self.solution_metadata.get("owner"),
            )
            if not result:
                continue
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=node.node_id)
                if not success:
                    raise DeploymentFailed(f"Failed to add node {node.node_id} to network {wid}", wid=wid)
            self.network_view = self.network_view.copy()

        # get ip addresses
        self.ip_addresses = []
        master_free_ips = self.network_view.get_node_free_ips(self.selected_nodes[0])
        self.ip_addresses.append(
            self.drop_down_choice(
                "Please choose IP Address for Master node", master_free_ips, required=True, default=master_free_ips[0]
            )
        )
        self.network_view.used_ips.append(self.ip_addresses[0])
        for i in range(1, len(self.selected_nodes)):
            free_ips = self.network_view.get_node_free_ips(self.selected_nodes[i])
            self.ip_addresses.append(
                self.drop_down_choice(
                    f"Please choose IP Address for Slave node {i}", free_ips, required=True, default=free_ips[0]
                )
            )
            self.network_view.used_ips.append(self.ip_addresses[i])

    @chatflow_step(title="Cluster reservations", disable_previous=True)
    @deployment_context()
    def reservation(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "kubernetes", "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)
        self.reservations = deployer.deploy_kubernetes_cluster(
            pool_id=self.selected_pool_ids[0],
            node_ids=[n.node_id for n in self.selected_nodes],
            network_name=self.network_view.name,
            cluster_secret=self.cluster_secret,
            ssh_keys=self.ssh_keys,
            size=self.cluster_size,
            ip_addresses=self.ip_addresses,
            slave_pool_ids=self.selected_pool_ids[1:],
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )

        for resv in self.reservations:
            success = deployer.wait_workload(resv["reservation_id"], self)
            if not success:
                raise DeploymentFailed(
                    f"Failed to deploy workload {resv['reservation_id']}",
                    solution_uuid=self.solution_id,
                    wid=resv["reservation_id"],
                )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        res = f"""\
        # Kubernetes cluster has been deployed successfully:
        <br />\n
        - Master
            - IP: {self.reservations[0]["ip_address"]}
            - To connect: `ssh rancher@{self.reservations[0]["ip_address"]}`
        <br />\n

        """
        res = dedent(res)
        worker_res = ""
        for idx, resv in enumerate(self.reservations[1:]):
            worker_res += f"""\
            \n
            - Worker {idx + 1}
                - IP: {resv["ip_address"]}
                - To connect: `ssh rancher@{resv["ip_address"]}`
            <br />\n
            """
        self.md_show(res + dedent(worker_res))


chat = KubernetesDeploy
