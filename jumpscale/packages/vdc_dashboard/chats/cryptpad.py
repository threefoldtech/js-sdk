from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class CryptpadDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "cryptpad"
    title = "Cryptpad"
    HELM_REPO_NAME = "marketplace"
    DOMAIN_KEY_IN_CHART_VALUES = "ingress.host"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "set_config",
        "create_subdomain",
        "install_chart",
        "initializing",
        "success",
    ]

    def get_extra_config(self):
        return {
            "ingress.host": self.config.chart_config.domain,
            "volume.size": self.config.chart_config.volume_size,
            "volume.hostPath": f"/cryptpad/{self.config.release_name}",
        }

    @chatflow_step(title="Configurations")
    def set_config(self):
        # TODO: get config from user
        choices = ["10", "15", "20"]
        self.config.chart_config.volume_size = self.single_choice(
            "Please select your storage size (in GBs)", choices, required=True, default="10",
        )


chat = CryptpadDeploy
