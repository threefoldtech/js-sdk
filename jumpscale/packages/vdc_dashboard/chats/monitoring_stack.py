from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.sals.marketplace import deployer
from jumpscale.sals.reservation_chatflow import DeploymentFailed


class InstallMonitoringStack(SolutionsChatflowDeploy):
    title = "Monitoring Stack"
    steps = ["confirm", "success"]
    SOLUTION_TYPE = "monitoring-stack"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "get_release_name",
        "create_prometheus_subdomain",
        "create_grafane_subdomain",
        "set_config",
        "install_chart",
        "initializing",
        "success",
    ]

    @chatflow_step(title="Create Prometheus subdomain")
    def create_prometheus_subdomain(self):
        {super().create_subdomain()}

    @chatflow_step(title="Create Grafana subdomain")
    def create_grafane_subdomain(self):
        self.workload_ids = []
        metadata = {
            "name": self.release_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.release_name},
        }
        self.grafana_domain = f"grafana-{self.domain}"
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.grafana_domain,
                addresses=[self.vdc_info["public_ip"]],
                solution_uuid=self.solution_id,
                identity_name=self.identity_name,
                **metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[0], self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.grafana_domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}. The resources you paid for will be re-used in your upcoming deployments.",
                wid=self.workload_ids[0],
            )

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()
        self.chart_config = {
            "prometheus.ingress.hosts[0]": self.domain,
            "grafana.ingress.hosts[0]": self.grafana_domain,
        }

    @chatflow_step
    def success(self):
        extra_info = f"Grafana can be accessed by {self.grafana_domain}"
        super.success(extra_info=extra_info)


chat = InstallMonitoringStack
