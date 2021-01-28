from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import CHART_LIMITS, SolutionsChatflowDeploy


class DigibyteDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "digibyte"
    title = "Digibyte"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    CHART_LIMITS = {
        "Silver": {"cpu": "2000m", "memory": "2024Mi"},
        "Gold": {"cpu": "3000m", "memory": "3072Mi"},
        "Platinum": {"cpu": "4000m", "memory": "4096Mi"},
    }

    def _enter_credentials(self):

        form = self.new_form()
        self.rpcuser = form.string_ask("Please enter the rpcname.", required=True)
        self.rpcpassword = form.secret_ask("Please enter the rpcpassword", required=True)
        form.ask()
        self.rpcuser = self.rpcuser.value
        self.rpcpassword = self.rpcpassword.value

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._enter_credentials()
        self._choose_flavor(CHART_LIMITS)
        self.vdc.get_deployer().kubernetes.add_traefik_entrypoint("digibyte-rpc", "14022")
        self.vdc.get_deployer().kubernetes.add_traefik_entrypoint("digibyte-p2p", "12024")

        self.chart_config.update(
            {
                "env.rpcuser": self.rpcuser,
                "env.rpcpassword": self.rpcpassword,
                "global.ingress.host": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = DigibyteDeploy
