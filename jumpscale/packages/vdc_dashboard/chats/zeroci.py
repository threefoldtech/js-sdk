from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class ZeroCIDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "zeroci"
    title = "ZeroCI"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):
        # TODO: get config from user
        self._choose_flavor()
        self.chart_config.update(
            {
                "ingress.hosts[0].host": self.domain,
                "ingress.hosts[0].paths[0]": "/",
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
                "volumes.bin": f"/zeroci/{self.release_name}/bin",
                "volumes.redis": f"/zeroci/{self.release_name}/redis",
                "volumes.persistent": f"/zeroci/{self.release_name}/persistent",
            }
        )


chat = ZeroCIDeploy
