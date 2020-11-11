from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployer
from .base_component import VDCBaseComponent
from .size import *


class VDCKubernetesDeployer(VDCBaseComponent):
    def deploy_kubernetes(self, pool_id, scheduler, k8s_size_dict, cluster_secret, ssh_keys, vdc_uuid):
        no_nodes = k8s_size_dict["no_nodes"]
        master_ip = None
        network_view = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
        nodes_generator = scheduler.nodes_by_capacity(**K8S_SIZES[k8s_size_dict["size"]])

        # deploy master
        master_ip = self._deploy_master(
            pool_id, nodes_generator, k8s_size_dict, cluster_secret, ssh_keys, vdc_uuid, network_view
        )
        if not master_ip:
            return
        return self.add_workers(
            pool_id,
            nodes_generator,
            k8s_size_dict,
            cluster_secret,
            ssh_keys,
            vdc_uuid,
            network_view,
            master_ip,
            no_nodes,
        )

    def _deploy_master(self, pool_id, nodes_generator, k8s_size_dict, cluster_secret, ssh_keys, vdc_uuid, network_view):
        master_ip = None
        # deploy_master
        while not master_ip:
            try:
                master_node = next(nodes_generator)
                j.logger.info(f"VDC: NEW K8S: node {master_node.node_id} selected")
                # add node to network
                try:
                    result = deployer.add_network_node(
                        self.vdc_name, master_node, pool_id, network_view, self.bot, self.identity.instance_name
                    )
                    if result:
                        for wid in result["ids"]:
                            success = deployer.wait_workload(
                                wid, self.bot, 3, identity_name=self.identity.instance_name
                            )
                            if not success:
                                continue
                except DeploymentFailed:
                    continue
            except IndexError:
                raise j.exceptions.Runtime("all tries to deploy k8s master node have failed")

            # deploy master
            network_view = network_view.copy()
            ip_address = network_view.get_free_ip(master_node)
            wid = deployer.deploy_kubernetes_master(
                pool_id,
                master_node.node_id,
                network_view.name,
                cluster_secret,
                ssh_keys,
                ip_address,
                size=k8s_size_dict["size"].value,
                secret=cluster_secret,
                identity_name=self.identity.instance_name,
                form_info={"chatflow": "kubernetes"},
                name=self.vdc_name,
                solution_uuid=vdc_uuid,
            )
            try:
                success = deployer.wait_workload(wid, self.bot, identity_name=self.identity.instance_name)
                if not success:
                    continue
                master_ip = ip_address
                return master_ip
            except DeploymentFailed:
                continue

    def _add_nodes_to_network(self, pool_id, nodes_generator, wids, no_nodes, network_view):
        deployment_nodes = []
        for node in nodes_generator:
            j.logger.info(f"VDC: NEW K8S: node {node.node_id} selected")
            if len(deployment_nodes) < no_nodes - len(wids):
                deployment_nodes.append(node)
                continue
            # add nodes to network
            network_view = network_view.copy()
            result = []
            try:
                network_result = deployer.add_multiple_network_nodes(
                    self.vdc_name,
                    [node.node_id for node in deployment_nodes],
                    [pool_id] * len(deployment_nodes),
                    network_view,
                    self.bot,
                    self.identity.instance_name,
                )

                if network_result:
                    result += network_result["ids"]
                for wid in result:
                    try:
                        success = deployer.wait_workload(wid, self.bot, 5, identity_name=self.identity.instance_name)
                        if not success:
                            raise DeploymentFailed()
                    except DeploymentFailed:
                        # for failed network deployments
                        workload = self.zos.workloads.get(wid)
                        success_nodes = []
                        for d_node in deployment_nodes:
                            if d_node.node_id == workload.info.node_id:
                                continue
                            success_nodes.append(node)
                        deployment_nodes = success_nodes
            except DeploymentFailed as e:
                # for dry run exceptions
                if e.wid:
                    workload = self.zos.workloads.get(e.wid)
                    success_nodes = []
                    for d_node in deployment_nodes:
                        if d_node.node_id == workload.info.node_id:
                            continue
                        success_nodes.append(node)
                    deployment_nodes = success_nodes
                else:
                    deployment_nodes = []
                continue
            if len(deployment_nodes) == no_nodes:
                return deployment_nodes

    def add_workers(
        self,
        pool_id,
        nodes_generator,
        k8s_size_dict,
        cluster_secret,
        ssh_keys,
        vdc_uuid,
        network_view,
        master_ip,
        no_nodes,
    ):
        # deploy workers
        wids = []
        result = []
        for _ in range(15):
            deployment_nodes = self._add_nodes_to_network(pool_id, nodes_generator, wids, no_nodes, network_view)
            if not deployment_nodes:
                return
            network_view = network_view.copy()
            # deploy workers
            for node in deployment_nodes:
                ip_address = network_view.get_free_ip(node)
                result.append(
                    deployer.deploy_kubernetes_worker(
                        pool_id,
                        node.node_id,
                        network_view.name,
                        cluster_secret,
                        ssh_keys,
                        ip_address,
                        master_ip,
                        size=k8s_size_dict["size"].value,
                        secret=cluster_secret,
                        identity_name=self.identity.instance_name,
                        form_info={"chatflow": "kubernetes"},
                        name=self.vdc_name,
                        solution_uuid=vdc_uuid,
                    )
                )
            for wid in result:
                try:
                    success = deployer.wait_workload(wid, self.bot, identity_name=self.identity.instance_name)
                    if not success:
                        continue
                    wids.append(wid)
                except DeploymentFailed:
                    pass

            if len(wids) == no_nodes:
                return wids
