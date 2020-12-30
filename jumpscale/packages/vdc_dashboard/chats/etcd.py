from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class EtcdDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "etcd"
    title = "ETCD"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):
        self.resources_limits = {
            "cpu": 0,
            "memory": 0,
        }
        form = self.new_form()
        self.no_replicas = form.int_ask("Enter number of etcd nodes", default=1, required=True, min=100)
        self.resources_limits["cpu"] = form.int_ask(
            "Enter limit for cpu in millicpu", default=250, required=True, min=100
        )
        self.resources_limits["memory"] = form.int_ask(
            "Enter limit for memory in Mi", default=256, required=True, min=128
        )
        self.pvc_size = form.int_ask("Enter size of PVC in Gi", default=8, required=True, min=1)
        form.ask(
            "Visit https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#resource-units-in-kubernetes for more info about units"
        )
        self.chart_config.update(
            {
                "statefulset.replicaCount": self.no_replicas,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
                "persistence.size": self.pvc_size,
                "disasterRecovery.pvc.size": self.pvc_size / 4,
            }
        )


chat = EtcdDeploy
