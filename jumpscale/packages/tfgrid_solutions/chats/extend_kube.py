from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer, DeploymentFailed
from jumpscale.clients.explorer.models import State
from jumpscale.clients.explorer.models import K8s


class ExtendKubernetesCluster(GedisChatBot):
    title = "Extend Kubernetes Cluster"
    steps = ["choose_nodes_cound", "choose_flavor", "add_public_ip", "add_nodes", "success"]
    KUBERNETES_SIZES = K8s.SIZES

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

    @chatflow_step(title="Public IP")
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
        if self.enable_public_ip:
            self.node_query["ipv4u"] = self.nodes_count
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
            network_view = network_view.copy()
            ip_address = network_view.get_free_ip(node)
            if not ip_address:
                raise StopChatFlow(f"No free IPs for network {network_name} on the specifed node" f" {node_id}")

            self.md_show_update(f"Deploying worker on node {node.node_id}")
            # Add public ip
            public_id_wid = 0
            if self.enable_public_ip:
                public_id_wid, _ = deployer.create_public_ip(
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

        self.success_workload_count = 0
        zos = j.sals.zos.get()
        for resv in self.reservations:
            try:
                success = deployer.wait_workload(resv, self, cancel_by_uuid=False)
                self.success_workload_count += 1
            except DeploymentFailed as ex:
                # Cleaning k8s workloads and public IP workloads in case of failure in deployment
                workload = zos.workloads.get(resv)
                if workload.public_ip:
                    zos.workloads.decomission(workload.public_ip)
                zos.workloads.decomission(wid)
                j.logger.error(f"Failed to deploy  workloads for {resv}, the error: {str(ex)}")

        if not self.success_workload_count:
            raise StopChatFlow(msg="Can't extend your cluster, please try again later")

        if self.success_workload_count < len(self.reservations):
            raise StopChatFlow(
                msg=f"Some nodes failed to extend, {self.success_workload_count} of {self.nodes_count}, please try again later"
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(
            f"Your cluster has been extended successfully with {self.nodes_count} Nodes, workload ids: {self.reservations}  "
        )


chat = ExtendKubernetesCluster
