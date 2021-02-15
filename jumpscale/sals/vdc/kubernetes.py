import math
import uuid

from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployer
from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed

from .base_component import VDCBaseComponent
from .scheduler import CapacityChecker, Scheduler
from .size import *
from jumpscale.clients.explorer.models import K8s, NextAction
import gevent


class VDCKubernetesDeployer(VDCBaseComponent):
    def __init__(self, *args, **kwrags) -> None:
        super().__init__(*args, **kwrags)

    def _preprare_extension_pool(self, farm_name, k8s_flavor, no_nodes, duration, public_ip=False):
        """
        returns pool id after extension with enough cloud units
        duration in seconds
        """
        self.vdc_deployer.info(
            f"preperaring pool for kubernetes cluster extension on farm {farm_name}, flavor: {k8s_flavor}, no_nodes: {no_nodes}, duration: {duration}, public_ip: {public_ip}"
        )
        k8s = K8s()
        k8s.size = k8s_flavor.value
        cloud_units = k8s.resource_units().cloud_units()
        cus = int(cloud_units.cu * duration * no_nodes)
        sus = int(cloud_units.su * duration * no_nodes)
        ipv4us = 0
        if public_ip:
            ipv4us = int(duration)

        farm = self.explorer.farms.get(farm_name=farm_name)
        pool_id = None
        self.vdc_deployer.info(f"kubernetes cluster extension: searching for existing pool on farm {farm_name}")
        for pool in self.zos.pools.list():
            farm_id = deployer.get_pool_farm_id(pool.pool_id, pool, self.identity.instance_name)
            if farm_id == farm.id:
                pool_id = pool.pool_id
                break

        if not pool_id:
            pool_info = self.vdc_deployer._retry_call(
                self.zos.pools.create,
                args=[math.ceil(cus), math.ceil(sus), ipv4us, farm_name, ["TFT"], j.core.identity.me],
            )
            pool_id = pool_info.reservation_id
            self.vdc_deployer.info(f"kubernetes cluster extension: creating a new pool {pool_id}")
            self.vdc_deployer.info(f"new pool {pool_info.reservation_id} for kubernetes cluster extension.")
        else:
            self.vdc_deployer.info(f"kubernetes cluster extension: found pool {pool_id}")
            node_ids = [node.node_id for node in self.zos.nodes_finder.nodes_search(farm_name=farm_name)]
            pool_info = self.vdc_deployer._retry_call(
                self.zos.pools.extend, args=[pool_id, cus, sus, ipv4us], kwargs={"node_ids": node_ids}
            )
            self.vdc_deployer.info(
                f"using pool {pool_id} extension reservation: {pool_info.reservation_id} for kubernetes cluster extension."
            )

        self.vdc_deployer.pay(pool_info)

        success = self.vdc_deployer.wait_pool_payment(pool_info.reservation_id)
        if not success:
            raise j.exceptions.Runtime(f"Pool {pool_info.reservation_id} resource reservation timedout")

        return pool_id

    def extend_cluster(
        self,
        farm_name,
        master_ip,
        k8s_flavor,
        cluster_secret,
        ssh_keys,
        no_nodes=1,
        duration=None,
        public_ip=False,
        solution_uuid=None,
        external=True,
    ):
        """
        search for a pool in the same farm and extend it or create a new one with the required capacity
        """
        old_node_ids = []
        for k8s_node in self.vdc_instance.kubernetes:
            old_node_ids.append(k8s_node.node_id)
        cc = CapacityChecker(farm_name)
        cc.exclude_nodes(*old_node_ids)

        for _ in range(no_nodes):
            if not cc.add_query(**VDC_SIZE.K8S_SIZES[k8s_flavor]):
                raise j.exceptions.Validation(
                    f"not enough capacity in farm {farm_name} for {no_nodes} kubernetes nodes of flavor {k8s_flavor}"
                )

        duration = (
            duration * 60 * 60 * 24
            if duration
            else self.vdc_instance.expiration_date.timestamp() - j.data.time.utcnow().timestamp
        )
        if duration <= 0:
            raise j.exceptions.Validation(f"invalid duration {duration}")
        pool_id = self._preprare_extension_pool(farm_name, k8s_flavor, no_nodes, duration, public_ip)
        scheduler = Scheduler(pool_id=pool_id)
        scheduler.exclude_nodes(*old_node_ids)
        network_view = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
        nodes_generator = scheduler.nodes_by_capacity(**VDC_SIZE.K8S_SIZES[k8s_flavor], public_ip=public_ip)
        solution_uuid = solution_uuid or uuid.uuid4().hex
        wids = self._add_workers(
            pool_id,
            nodes_generator,
            k8s_flavor,
            cluster_secret,
            ssh_keys,
            solution_uuid,  # use differnet uuid than
            network_view,
            master_ip,
            no_nodes,
            public_ip,
            external,
        )
        if not wids:
            self.vdc_deployer.error(f"failed to extend kubernetes cluster with {no_nodes} nodes of flavor {k8s_flavor}")
            j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(solution_uuid)
            raise j.exceptions.Runtime(
                f"failed to extend kubernetes cluster with {no_nodes} nodes of flavor {k8s_flavor}"
            )
        return wids

    def deploy_master(self, pool_id, scheduler, k8s_flavor, cluster_secret, ssh_keys, solution_uuid, network_view):
        master_ip = None
        # deploy_master
        k8s_resources_dict = VDC_SIZE.K8S_SIZES[k8s_flavor]
        nodes_generator = scheduler.nodes_by_capacity(**k8s_resources_dict, pool_id=pool_id, public_ip=True)
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
                                wid, self.bot, 3, identity_name=self.identity.instance_name, cancel_by_uuid=False
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
                self.vdc_deployer.error("all tries to deploy kubernetes master node have failed")
                raise j.exceptions.Runtime("all tries to deploy kubernetes master node have failed")

            # reserve public_ip
            public_ip_wid = self.vdc_deployer.public_ip.get_public_ip(
                pool_id, master_node.node_id, solution_uuid=solution_uuid
            )
            if not public_ip_wid:
                self.vdc_deployer.error(f"failed to deploy reserve public ip on node {master_node.node_id}")
                continue

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
                size=k8s_flavor.value,
                identity_name=self.identity.instance_name,
                # form_info={"chatflow": "kubernetes"},
                # name=self.vdc_name,
                secret=cluster_secret,
                solution_uuid=solution_uuid,
                description=self.vdc_deployer.description,
                public_ip_wid=public_ip_wid,
            )
            self.vdc_deployer.info(f"kubernetes master wid: {wid}")
            try:
                success = deployer.wait_workload(
                    wid, self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                )
                if not success:
                    raise DeploymentFailed()
                master_ip = ip_address
                return master_ip
            except DeploymentFailed:
                self.zos.workloads.decomission(public_ip_wid)
                self.vdc_deployer.error(f"failed to deploy kubernetes master wid: {wid}")
                continue
        self.vdc_deployer.error("all tries to deploy kubernetes master have failed")

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
                        success = deployer.wait_workload(
                            wid, self.bot, 5, identity_name=self.identity.instance_name, cancel_by_uuid=False
                        )
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

    def _add_workers(
        self,
        pool_id,
        nodes_generator,
        k8s_flavor,
        cluster_secret,
        ssh_keys,
        solution_uuid,
        network_view,
        master_ip,
        no_nodes,
        public_ip=False,
        external=True,
    ):
        # deploy workers
        wids = []
        while True:
            result = []
            public_wids = []
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
                if public_ip:
                    public_ip_wid = self.vdc_deployer.public_ip.get_public_ip(pool_id, node.node_id, solution_uuid)
                    if not public_ip_wid:
                        self.vdc_deployer.error(f"failed to deploy reserve public ip on node {node.node_id}")
                        continue
                else:
                    public_ip_wid = 0
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
                        size=k8s_flavor.value,
                        secret=cluster_secret,
                        identity_name=self.identity.instance_name,
                        # form_info={"chatflow": "kubernetes"},
                        # name=self.vdc_name,
                        solution_uuid=solution_uuid,
                        description=self.vdc_deployer.description,
                        public_ip_wid=public_ip_wid,
                        external=external,
                    )
                )
                public_wids.append(public_ip_wid)
            for idx, wid in enumerate(result):
                try:
                    success = deployer.wait_workload(
                        wid, self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                    )
                    if not success:
                        raise DeploymentFailed()
                    wids.append(wid)
                    self.vdc_deployer.info(f"kubernetes worker deployed sucessfully wid: {wid}")
                except DeploymentFailed:
                    if public_wids[idx]:
                        self.zos.workloads.decomission(public_wids[idx])
                    self.vdc_deployer.error(f"failed to deploy kubernetes worker wid: {wid}")

            self.vdc_deployer.info(f"successful kubernetes workers ids: {wids}")
            if len(wids) == no_nodes:
                self.vdc_deployer.info(f"all workers deployed successfully")
                return wids
        self.vdc_deployer.error("all tries to deploy kubernetes workers have failed")

    def download_kube_config(self, master_ip):
        """
        Args:
            master ip: public ip address of kubernetes master
        """
        j.sals.nettools.wait_connection_test(master_ip, 22)
        ssh_client = j.clients.sshclient.get(self.vdc_name, user="rancher", host=master_ip, sshkey=self.vdc_name)
        rc, out, err = ssh_client.sshclient.run("cat /etc/rancher/k3s/k3s.yaml", warn=True)
        if rc:
            j.logger.error(f"couldn't read k3s config for VDC {self.vdc_name}")
            j.tools.alerthandler.alert_raise(
                "vdc", f"couldn't read k3s config for VDC {self.vdc_name} rc: {rc}, out: {out}, err: {err}"
            )
            raise j.exceptions.Runtime(f"Couldn't download kube config for vdc: {self.vdc_name}.")
        j.clients.sshclient.delete(ssh_client.instance_name)
        config_dict = j.data.serializers.yaml.loads(out)
        config_dict["clusters"][0]["cluster"]["server"] = f"https://{master_ip}:6443"
        out = j.data.serializers.yaml.dumps(config_dict)
        j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/kube/{self.vdc_deployer.tname}")
        j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/kube/{self.vdc_deployer.tname}/{self.vdc_name}.yaml", out)
        return out

    def delete_worker(self, wid):
        workloads_to_delete = []
        workload = self.zos.workloads.get(wid)
        if not workload.master_ips:
            raise j.exceptions.Input("can't delete controller node")
        if workload.info.next_action == NextAction.DEPLOY:
            workloads_to_delete.append(wid)
        if workload.public_ip:
            public_ip_workload = self.zos.workloads.get(workload.public_ip)
            if public_ip_workload.info.next_action == NextAction.DEPLOY:
                workloads_to_delete.append(public_ip_workload.id)
        for wid in workloads_to_delete:
            self.zos.workloads.decomission(wid)
        return workloads_to_delete

    # TODO: better implementatiom
    def upgrade_traefik(self):
        """
        Upgrades traefik chart installed on k3s to v2.3.3 to support different CAs
        """

        def is_traefik_installed(manager):
            releases = manager.list_deployed_releases("kube-system")
            # TODO: List only using names
            for release in releases:
                if release.get("name") == "traefik":
                    return True
            return False

        kubeconfig_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{self.vdc_deployer.tname}/{self.vdc_name}.yaml"
        k8s_client = j.sals.kubernetes.Manager(config_path=kubeconfig_path)
        k8s_client.add_helm_repo("traefik", "https://helm.traefik.io/traefik")
        k8s_client.update_repos()

        # wait until traefik chart is installed on the cluster then uninstall it
        checks = 12
        while checks > 0 and not is_traefik_installed(k8s_client):
            gevent.sleep(5)
            checks -= 1
        if is_traefik_installed(k8s_client):
            k8s_client.delete_deployed_release("traefik", "kube-system")

        # install traefik v2.3.3 chart
        # TODO: better code for the values
        k8s_client.install_chart(
            "traefik",
            "traefik/traefik",
            "kube-system",
            chart_values_file="""<(echo -e 'image:
  tag: "2.3.3"
additionalArguments:
  - "--certificatesresolvers.default.acme.tlschallenge"
  - "--certificatesresolvers.default.acme.email=dsafsdajfksdhfkjadsfoo@you.com"
  - "--certificatesresolvers.default.acme.storage=/data/acme.json"
  - "--certificatesresolvers.default.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
  - "--certificatesresolvers.default.acme.httpchallenge.entrypoint=web"
  - "--certificatesresolvers.gridca.acme.tlschallenge"
  - "--certificatesresolvers.gridca.acme.email=dsafsdajfksdhfkjadsfoo@you.com"
  - "--certificatesresolvers.gridca.acme.storage=/data/acme1.json"
  - "--certificatesresolvers.gridca.acme.caserver=https://ca1.grid.tf"
  - "--certificatesresolvers.gridca.acme.httpchallenge.entrypoint=web"
  - "--certificatesresolvers.le.acme.tlschallenge"
  - "--certificatesresolvers.le.acme.email=dsafsdajfksdhfkjadsfoo@you.com"
  - "--certificatesresolvers.le.acme.storage=/data/acme2.json"
  - "--certificatesresolvers.le.acme.caserver=https://acme-v02.api.letsencrypt.org/directory"
  - "--certificatesresolvers.le.acme.httpchallenge.entrypoint=web"
ports:
  web:
    redirectTo: websecure
  websecure:
    tls:
      enabled: true')""",
        )

    def add_traefik_entrypoint(self, entrypoint_name, port, expose=True, protocol="TCP"):
        """
        Add a new entrypoint to traefik or override an existing one
        """

        kubeconfig_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{self.vdc_deployer.tname}/{self.vdc_name}.yaml"
        k8s_client = j.sals.kubernetes.Manager(config_path=kubeconfig_path)
        k8s_client.add_helm_repo("traefik", "https://helm.traefik.io/traefik")
        k8s_client.update_repos()
        config_str = k8s_client.get_helm_chart_user_values("traefik", "kube-system")
        config_json = j.data.serializers.json.loads(config_str)
        config_json["ports"][entrypoint_name] = {
            "port": port,
            "exposedPort": port,
            "expose": expose,
            "protocol": protocol,
        }
        config_yaml = j.data.serializers.yaml.dumps(config_json)
        k8s_client.upgrade_release("traefik", "traefik/traefik", "kube-system", config_yaml)
