from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class ZeroCIDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "zeroci"
    title = "ZeroCI"
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

    def get_config(self):
        return {
            "ingress.hosts[0].host": self.config.chart_config.domain,
            "ingress.hosts[0].paths[0]": "/",
            "volumes.bin": f"/zeroci/{self.config.release_name}/bin",
            "volumes.redis": f"/zeroci/{self.config.release_name}/redis",
            "volumes.persistent": f"/zeroci/{self.config.release_name}/persistent",
        }


chat = ZeroCIDeploy
