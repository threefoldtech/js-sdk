from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployer
from .base_component import VDCBaseComponent
from .size import *
from .scheduler import Scheduler
import os


class VDCKubernetesDeployer(VDCBaseComponent):
    def __init__(self, *args, **kwrags) -> None:
        super().__init__(*args, **kwrags)

    def deploy_kubernetes(self, pool_id, scheduler, k8s_size_dict, cluster_secret, ssh_keys, vdc_uuid):
        self.vdc_deployer.info(f"deploying kubernetes with size_dict: {k8s_size_dict}")
        no_nodes = k8s_size_dict["no_nodes"]
        master_ip = None
        network_view = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
        nodes_generator = scheduler.nodes_by_capacity(**K8S_SIZES[k8s_size_dict["size"]])

        # deploy master
        master_ip = self._deploy_master(
            pool_id, nodes_generator, k8s_size_dict, cluster_secret, ssh_keys, vdc_uuid, network_view
        )
        self.vdc_deployer.info(f"kubernetes master ip: {master_ip}")
        if not master_ip:
            self.vdc_deployer.error("failed to deploy master")
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

    def _deploy_master(
        self, pool_id, nodes_generator, k8s_size_dict, cluster_secret, ssh_keys, solution_uuid, network_view
    ):
        master_ip = None
        # deploy_master
        while not master_ip:
            try:
                try:
                    master_node = next(nodes_generator)
                except StopIteration:
                    return
                self.vdc_deployer.info(f"deploying kubernetes master on node {master_node.node_id}")
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
                                self.vdc_deployer.error(f"failed to deploy network for kubernetes master wid: {wid}")
                                raise DeploymentFailed
                except DeploymentFailed:
                    self.vdc_deployer.error(
                        f"failed to deploy network for kubernetes master on node {master_node.node_id}"
                    )
                    continue
            except IndexError:
                self.vdc_deployer.error("all tries to deploy k8s master node have failed")
                raise j.exceptions.Runtime("all tries to deploy k8s master node have failed")

            # deploy master
            network_view = network_view.copy()
            ip_address = network_view.get_free_ip(master_node)
            self.vdc_deployer.info(f"kubernetes master ip: {ip_address}")
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
                solution_uuid=solution_uuid,
                description=self.vdc_deployer.description,
            )
            self.vdc_deployer.info(f"kubernetes master wid: {wid}")
            try:
                success = deployer.wait_workload(wid, self.bot, identity_name=self.identity.instance_name)
                if not success:
                    raise DeploymentFailed()
                master_ip = ip_address
                return master_ip
            except DeploymentFailed:
                self.vdc_deployer.error(f"failed to deploy kubernetes master wid: {wid}")
                continue

    def _add_nodes_to_network(self, pool_id, nodes_generator, wids, no_nodes, network_view):
        deployment_nodes = []
        self.vdc_deployer.info(f"adding nodes to network. no_nodes: {no_nodes}, wids: {wids}")
        for node in nodes_generator:
            self.vdc_deployer.info(f"node {node.node_id} selected")
            deployment_nodes.append(node)
            if len(deployment_nodes) < no_nodes - len(wids):
                continue
            self.vdc_deployer.info(f"adding nodes {[node.node_id for node in deployment_nodes]} to network")
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
                self.vdc_deployer.info(f"network update result: {network_result}")

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
                        self.vdc_deployer.error(f"failed to add node {workload.info.node_id} to network. wid: {wid}")
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
                    self.vdc_deployer.error(f"failed to add node {workload.info.node_id} to network. wid: {e.wid}")
                    success_nodes = []
                    for d_node in deployment_nodes:
                        if d_node.node_id == workload.info.node_id:
                            continue
                        success_nodes.append(node)
                    deployment_nodes = success_nodes
                else:
                    self.vdc_deployer.error(f"network deployment failed on multiple nodes due to error {str(e)}")
                    deployment_nodes = []
                continue
            if len(deployment_nodes) == no_nodes:
                self.vdc_deployer.info("required nodes added to network successfully")
                return deployment_nodes

    def add_workers(
        self,
        pool_id,
        nodes_generator,
        k8s_size_dict,
        cluster_secret,
        ssh_keys,
        solution_uuid,
        network_view,
        master_ip,
        no_nodes,
    ):
        # deploy workers
        wids = []
        while True:
            result = []
            deployment_nodes = self._add_nodes_to_network(pool_id, nodes_generator, wids, no_nodes, network_view)
            if not deployment_nodes:
                self.vdc_deployer.error("no available nodes to deploy kubernetes workers")
                return
            self.vdc_deployer.info(
                f"deploying kubernetes workers on nodes {[node.node_id for node in deployment_nodes]}"
            )
            network_view = network_view.copy()
            # deploy workers
            for node in deployment_nodes:
                self.vdc_deployer.info(f"deploying kubernetes worker on node {node.node_id}")
                ip_address = network_view.get_free_ip(node)
                self.vdc_deployer.info(f"kubernetes worker ip address: {ip_address}")
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
                        solution_uuid=solution_uuid,
                        description=self.vdc_deployer.description,
                    )
                )
            for wid in result:
                try:
                    success = deployer.wait_workload(wid, self.bot, identity_name=self.identity.instance_name)
                    if not success:
                        raise DeploymentFailed()
                    wids.append(wid)
                    self.vdc_deployer.info(f"kubernetes worker deployed sucessfully wid: {wid}")
                except DeploymentFailed:
                    self.vdc_deployer.error(f"failed to deploy kubernetes worker wid: {wid}")
                    pass

            self.vdc_deployer.info(f"successful kubernetes workers ids: {wids}")
            if len(wids) == no_nodes:
                self.vdc_deployer.info(f"all workers deployed successfully")
                return wids

    def get_ssh_client(self, master_ip):
        client = j.clients.sshclient.get(self.vdc_name, user="rancher", host=master_ip, sshkey=self.vdc_name)
        return client

    def download_kube_config(self, master_ip):
        """
        Args:
            master ip: public ip address of kubernetes master
        """
        ssh_client = self.get_ssh_client(master_ip)
        rc, out, err = ssh_client.run("cat /etc/rancher/k3s/k3s.yaml")
        if rc:
            j.logger.error(f"couldn't read k3s config for vdc {self.vdc_name}")
            j.tools.alerthandler.alert_raise(
                "vdc", f"couldn't read k3s config for vdc {self.vdc_name} rc: {rc}, out: {out}, err: {err}"
            )
            raise j.exceptions.Runtime(f"Couldn't download kube config for vdc: {self.vdc_name}.")

        j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/kube/{self.vdc_deployer.tname}")
        j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/kube/{self.vdc_deployer.tname}/{self.vdc_name}.yaml", out)
        return out
