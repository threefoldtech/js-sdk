from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy

CHART_LIMITS = {
    "Silver": {"cpu": "100m", "memory": "128Mi", "no_nodes": "1", "volume_size": "2Gi"},
    "Gold": {"cpu": "100m", "memory": "128Mi", "no_nodes": "3", "volume_size": "4Gi"},
    "Platinum": {"cpu": "250m", "memory": "256Mi", "no_nodes": "3", "volume_size": "8Gi"},
}

RESOURCE_VALUE_TEMPLATE = {
    "cpu": "CPU {}",
    "memory": "Memory {}",
    "no_nodes": "Number of Nodes {}",
    "volume_size": "Volume {}",
}


class EtcdDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "etcd"
    title = "ETCD"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "set_config", "install_chart", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor(CHART_LIMITS, RESOURCE_VALUE_TEMPLATE)
        self.chart_config.update(
            {
                "statefulset.replicaCount": self.resources_limits["no_nodes"],
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
                "persistence.size": self.resources_limits["volume_size"],
                "auth.rbac.enabled": "false",
                "metrics.enabled": "true",
            }
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):

        replicas_name = [f"<br />-{self.release_name}-{i}" for i in range(int(self.resources_limits["no_nodes"]))]
        message = f"""\
        # You deployed a new instance {self.release_name} of {self.SOLUTION_TYPE}
        <br />\n
        - etcd can be accessed via port 2379 on the following DNS name from within your cluster:
            {self.release_name}.default.svc.cluster.local

        - Your PODNAME one of the following:
            {''.join(replicas_name)}
        - To set a key run the following command:
            `kubectl exec -it $PODNAME -- etcdctl put message Hello`

        - To get a key run the following command:
            `kubectl exec -it $PODNAME -- etcdctl get message`

        - To connect to your etcd server from outside the cluster execute the following commands:
            `kubectl port-forward --namespace default svc/{self.release_name} 2379:2379`

        - You can visit <a href="https://etcd.io/docs/v3.4.0/" target="_blank">ETCD Docs</a> for more information
        """
        self.md_show(dedent(message), md=True)


chat = EtcdDeploy
