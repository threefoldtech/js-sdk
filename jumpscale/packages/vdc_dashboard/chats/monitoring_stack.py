from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class InstallMonitoringStack(SolutionsChatflowDeploy):
    title = "Monitoring Stack"
    steps = ["confirm", "success"]
    SOLUTION_TYPE = "monitoring_stack"
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
        {super().create_subdomain()}

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()
        prometheus_domain = self.domain
        grafana_domain = self.domain
        self.chart_config = {
            "prometheus.ingress.hosts[0]": prometheus_domain,
            "grafana.ingress.hosts[0]": grafana_domain,
        }


chat = InstallMonitoringStack
