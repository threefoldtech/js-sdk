from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class TaigaDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "taiga"
    title = "Taiga"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):

        self._choose_flavor()
        self.chart_config = {
            "domain": self.domain,
            "resources.limits.cpu": self.resources_limits["cpu"],
            "resources.limits.memory": self.resources_limits["memory"],
        }
        # subdomain selected on gateway on preferred farm
        if self.preferred_farm_gw:
            self.chart_config.update({"ingress.certresolver": "gridca"})


chat = TaigaDeploy
