from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.sals.marketplace import deployer
from jumpscale.sals.reservation_chatflow import DeploymentFailed
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class InstallMonitoringStack(SolutionsChatflowDeploy):
    title = "Monitoring Stack"
    steps = ["confirm", "success"]
    SOLUTION_TYPE = "monitoringstack"
    HELM_REPO_NAME = "marketplace"
    CHART_LIMITS = {
        "Silver": {"cpu": "1000m", "memory": "1536Mi"},
        "Gold": {"cpu": "2000m", "memory": "2048Mi"},
        "Platinum": {"cpu": "4000m", "memory": "4096Mi"},
    }

    steps = [
        "init_chatflow",
        "check_already_deployed",
        "get_release_name",
        "choose_flavor",
        "create_prometheus_subdomain",
        "create_grafane_subdomain",
        "install_chart",
        "initializing",
        "success",
    ]

    ADDITIONAL_QUERIES = [
        {"cpu": 100, "memory": 100},  # exporter
        {"cpu": 100, "memory": 25},  # alertmanager.config-reloader
        {"cpu": 100, "memory": 100},  # alertmanager.alertmanage
        {"cpu": 100, "memory": 25},  # prometheus.config-reloader
    ]

    def get_config(self):
        return {
            "prometheus.ingress.hosts[0]": self.config.chart_config.domain,
            "grafana.ingress.hosts[0]": self.config.chart_config.grafana_domain,
            "grafana.adminPassword": "prom-operator",
        }

    @chatflow_step(title="Checking deployed solutions")
    def check_already_deployed(self):
        if get_deployments(self.SOLUTION_TYPE, self.config.username):
            raise StopChatFlow("You can only have one Monitoring Stack solution per VDC")

    @chatflow_step(title="Create Prometheus subdomain")
    def create_prometheus_subdomain(self):
        super().create_subdomain()

    @chatflow_step(title="Create Grafana subdomain")
    def create_grafane_subdomain(self):
        self.workload_ids = []
        metadata = {
            "name": self.config.release_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.config.release_name},
        }
        self.config.chart_config.grafana_domain = f"grafana-{self.config.chart_config.domain}"
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.config.chart_config.grafana_domain,
                addresses=[self.vdc_info["public_ip"]],
                solution_uuid=self.solution_id,
                identity_name=self.identity_name,
                **metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[0], self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.config.chart_config.grafana_domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}. The resources you paid for will be re-used in your upcoming deployments.",
                wid=self.workload_ids[0],
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        extra_info = f'Grafana can be accessed by <a href="https://{self.config.chart_config.grafana_domain}" target="_blank">https://{self.config.chart_config.grafana_domain}</a>, user/pass: admin/prom-operator'
        super().success(extra_info=extra_info)


chat = InstallMonitoringStack
