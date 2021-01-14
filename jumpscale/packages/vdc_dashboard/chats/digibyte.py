from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class CryptpadDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "digibyte"
    title = "Digibyte"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()
        self.vdc.kubernetes.add_traefik_entrypoint("digibyte-rpc", "14022")
        self.vdc.kubernetes.add_traefik_entrypoint("digibyte-p2p", "12024")
        
        self.chart_config.update(
            {
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = DigibyteDeploy
