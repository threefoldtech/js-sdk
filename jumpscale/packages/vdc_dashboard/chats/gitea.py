from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class GiteaDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "gitea"
    title = "Gitea"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()
        self.chart_config = {
            "ingress.hosts[0]": self.domain,
            "ingress.certresolver": "default",
            "resources.limits.cpu": self.resources_limits["cpu"],
            "resources.limits.memory": self.resources_limits["memory"],
        }


chat = GiteaDeploy
