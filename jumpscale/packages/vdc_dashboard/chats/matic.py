from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class MaticDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "matic"
    title = "Matic"
    HELM_REPO_NAME = "marketplace"
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

    CHART_LIMITS = {
        "Silver": {"cpu": "2000m", "memory": "2024Mi"},
        "Gold": {"cpu": "4000m", "memory": "4096Mi"},
        "Platinum": {"cpu": "4000m", "memory": "8192Mi"},
    }

    def _check_uniqueness(self):
        if get_deployments(self.SOLUTION_TYPE, self.config.username):
            raise StopChatFlow("You can only have one Matic solution per VDC")

    def _enter_access_code(self):
        self.config.chart_config.access_code = self.secret_ask(
            "Enter Access Code. (This would be used to access your node's web page)", required=True
        )

    def _enter_rpc_url(self):
        self.config.chart_config.eth_rpc_url = self.string_ask(
            "Insert Infura or any full node RPC URL to Ethereum. You can skip this option if you are deploying a sentry node"
        )

    def get_config(self):
        return {
            "access_code": self.config.chart_config.access_code,
            "env.eth_rpc_url": self.config.chart_config.eth_rpc_url,
            "global.ingress.host": self.config.chart_config.domain,
        }

    def get_release_name(self):
        self._check_uniqueness()
        super().get_release_name()

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._enter_access_code()
        self._enter_rpc_url()
        self.vdc.get_deployer().kubernetes.add_traefik_entrypoints(
            {"matic-bor": {"port": "30303"}, "matic-heimdall": {"port": "26656"}}
        )


chat = MaticDeploy
