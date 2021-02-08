from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class CryptpadDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "cryptpad"
    title = "Cryptpad"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "get_release_name",
        "create_subdomain",
        "set_config",
        "install_chart",
        "initializing",
        "success",
    ]

    @chatflow_step(title="Configurations")
    def set_config(self):
        # TODO: get config from user
        self._choose_flavor()
        choices = ["10", "15", "20"]
        self.volume_size = self.single_choice(
            "Please select your storage size (in GBs)", choices, required=True, default="10",
        )
        self.chart_config.update(
            {
                "ingress.host": self.domain,
                "volume.size": self.volume_size,
                "volume.hostPath": f"/persistent-data/{self.release_name}",
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = CryptpadDeploy
