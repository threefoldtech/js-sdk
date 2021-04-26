from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class TaigaDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "taiga"
    title = "Taiga"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "create_subdomain",
        "install_chart",
        "initializing",
        "success",
    ]
    CHART_LIMITS = {
        "Silver": {"cpu": "3000m", "memory": "3024Mi"},
        "Gold": {"cpu": "4000m", "memory": "4096Mi"},
        "Platinum": {"cpu": "5000m", "memory": "5120Mi"},
    }

    def get_config(self):
        return {
            "ingress.host": self.config.chart_config.domain,
            "resources.cpu": self.config.chart_config.resources_limits["cpu"][:-1],  # remove units added in chart
            "resources.memory": self.config.chart_config.resources_limits["memory"][:-2],  # remove units added in chart
        }


chat = TaigaDeploy
