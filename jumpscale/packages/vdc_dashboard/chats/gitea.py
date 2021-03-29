from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class GiteaDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "gitea"
    title = "Gitea"
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
    ADDITIONAL_QUERIES = [{"cpu": 250, "memory": 256}, {"cpu": 250, "memory": 256}]  # memcached  # postgresql

    def get_config(self):
        return {
            "ingress.hosts[0]": self.config.chart_config.domain,
        }


chat = GiteaDeploy
