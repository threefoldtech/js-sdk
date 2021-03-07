from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class MaticDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "matic"
    title = "Matic"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    CHART_LIMITS = {
        "Silver": {"cpu": "2000m", "memory": "2024Mi"},
        "Gold": {"cpu": "3000m", "memory": "3072Mi"},
        "Platinum": {"cpu": "4000m", "memory": "4096Mi"},
    }

    def _check_uniqueness(self):
        username = self.user_info()["username"]
        self.md_show_update("Preparing the chatflow . .")
        if get_deployments(self.SOLUTION_TYPE, username):
            raise StopChatFlow("You can only have one Matic solution per VDC")

    def get_release_name(self):
        self._check_uniqueness()
        super().get_release_name()

    def _enter_access_code(self):
        self.access_code = self.secret_ask(
            "Enter Access Code. (This would be used to access your node's web page)", required=True
        )

    def _enter_rpc_url(self):
        self.eth_rpc_url = self.string_ask(
            "Insert Infura or any full node RPC URL to Ethereum. You can skip this option if you are deploying a sentry node"
        )

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._enter_access_code()
        self._enter_rpc_url()
        self._choose_flavor(self.CHART_LIMITS)
        self.vdc.get_deployer().kubernetes.add_traefik_entrypoints(
            {"matic-bor": {"port": "30303"}, "matic-heimdall": {"port": "26656"}}
        )

        self.chart_config.update(
            {
                "access_code": self.access_code,
                "env.eth_rpc_url": self.eth_rpc_url,
                "global.ingress.host": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = MaticDeploy
