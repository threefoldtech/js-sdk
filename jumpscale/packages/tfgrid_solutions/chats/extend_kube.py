from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer
from collections import OrderedDict
from jumpscale.clients.explorer.models import State


class ExtendKubernetesCluster(GedisChatBot):
    title = "Extend Kubernetes Cluster"
    steps = ["choose_nodes_cound", "choose_flavor", "add_public_ip", "add_nodes", "success"]
    KUBERNETES_SIZES = OrderedDict(
        {
            1: {"cru": 1, "mru": 2, "sru": 50},
            2: {"cru": 2, "mru": 4, "sru": 100},
            3: {"cru": 2, "mru": 8, "sru": 25},
            4: {"cru": 2, "mru": 8, "sru": 50},
            5: {"cru": 2, "mru": 8, "sru": 200},
            6: {"cru": 4, "mru": 16, "sru": 50},
            7: {"cru": 4, "mru": 16, "sru": 100},
            8: {"cru": 4, "mru": 16, "sru": 400},
            9: {"cru": 8, "mru": 32, "sru": 100},
            10: {"cru": 8, "mru": 32, "sru": 200},
            11: {"cru": 8, "mru": 32, "sru": 800},
            12: {"cru": 16, "mru": 64, "sru": 200},
            13: {"cru": 16, "mru": 64, "sru": 400},
            14: {"cru": 16, "mru": 64, "sru": 800},
            15: {"cru": 1, "mru": 2, "sru": 25},
            16: {"cru": 2, "mru": 4, "sru": 50},
            17: {"cru": 4, "mru": 8, "sru": 50},
            18: {"cru": 1, "mru": 1, "sru": 25},
        }
    )

    @chatflow_step(title="Choose nodes count")
    def choose_nodes_cound(self):
        self.master_wid = int(self.kwargs.get("master_wid", 0))
        self.nodes_count = self.int_ask("How many nodes you want to add?", default=1, required=True, min=1)

    @chatflow_step(title="Choose nodes flavor")
    def choose_flavor(self):
        form = self.new_form()
        sizes = [
            f"vCPU: {data.get('cru')}, RAM: {data.get('mru')} GiB, Disk Space {data.get('sru')} GiB"
            for data in self.KUBERNETES_SIZES.values()
        ]
        cluster_size_string = form.drop_down_choice("Choose the size of your nodes", sizes, default=sizes[0])
        form.ask()
        self.cluster_size = sizes.index(cluster_size_string.value) + 1
        self.node_query = self.KUBERNETES_SIZES.get(self.cluster_size)
        self.public_ip = False

    @chatflow_step(title="Public Ip")
    def add_public_ip(self):
        choices = ["No", "Yes"]
        choice = self.single_choice("Do you want to enable public IP", choices, default="No", required=True)
        self.enable_public_ip = False
        if choice == "Yes":
            self.enable_public_ip = True

    @chatflow_step(title="Adding nodes")
    def add_nodes(self):
        zos = j.sals.zos.get()
        workload = zos.workloads.get(self.master_wid)
        metadata = j.sals.reservation_chatflow.reservation_chatflow.decrypt_reservation_metadata(workload.info.metadata)
        metadata = j.data.serializers.json.loads(metadata)
        pool_id = workload.info.pool_id
        old_wids = j.sals.marketplace.solutions.get_workloads_by_uuid(metadata.get("solution_uuid"))
        old_nodes = [wid.info.node_id for wid in old_wids if wid.info.result.state == State.Ok]
        nodes, pools = deployer.ask_multi_pool_distribution(self, self.nodes_count + len(old_nodes), self.node_query)
        nodes_pools_zip = list(zip(nodes, pools))
        selected_nodes = list(filter(lambda x: x[0].node_id not in old_nodes, nodes_pools_zip))
        if len(selected_nodes) < self.nodes_count:
            self.stop(
                f"Failed to find resources to deploy {self.nodes_count}, available nodes are: {len(selected_nodes)}"
            )
        new_nodes = selected_nodes[: self.nodes_count]
        network_view = deployer.get_network_view(workload.network_id)
        master_ip = workload.ipaddress

        self.reservations = []
        for node, pool_id in new_nodes:
            res = deployer.add_network_node(workload.network_id, node, pool_id)
            if res:
                for wid in res["ids"]:
                    success = deployer.wait_workload(wid, breaking_node_id=node.node_id)
                    if not success:
                        raise StopChatFlow(f"Failed to add node {node.node_id} to network {wid}")
            ip_address = network_view.get_free_ip(node)
            if not ip_address:
                raise StopChatFlow(f"No free IPs for network {network_name} on the specifed node" f" {node_id}")

            self.md_show_update(f"Deploying worker on node {node}")
            # Add public ip
            public_id_wid = 0
            if self.enable_public_ip:
                public_id_wid = deployer.get_public_ip(
                    pool_id, node.node_id, solution_uuid=metadata.get("solution_uuid")
                )

            self.reservations.append(
                deployer.deploy_kubernetes_worker(
                    pool_id,
                    node.node_id,
                    workload.network_id,
                    workload.cluster_secret,
                    workload.ssh_keys,
                    ip_address,
                    master_ip,
                    size=self.cluster_size,
                    identity_name=None,
                    description="",
                    public_ip_wid=public_id_wid,
                    **metadata,
                )
            )

        for resv in self.reservations:
            success = deployer.wait_workload(resv, self)
            if not success:
                raise DeploymentFailed(
                    f"Failed to deploy workload {resv}", solution_uuid=self.solution_id, wid=resv,
                )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(f"Your cluster has been extended successfully with workload ids: {self.reservations}")


chat = ExtendKubernetesCluster
