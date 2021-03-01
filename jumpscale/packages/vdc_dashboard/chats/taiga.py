from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class TaigaDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "taiga"
    title = "Taiga"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]
    ADDITIONAL_QUERIES = [
        {"cpu": 250, "memory": 256},  # postgers
    ]

    @chatflow_step(title="Configurations")
    def set_config(self):

        self._choose_flavor()
        self.chart_config.update(
            {
                "domain": self.domain,
                "postgresql.fullnameOverride": f"taiga-postgresql-{self.release_name}",
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = TaigaDeploy
