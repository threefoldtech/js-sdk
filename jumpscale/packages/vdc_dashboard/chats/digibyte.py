from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class DigibyteDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "digibyte"
    title = "DigiByte"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "create_subdomain",
        "set_config",
        "install_chart",
        "initializing",
        "success",
    ]

    CHART_LIMITS = {
        "Silver": {"cpu": "2000m", "memory": "2024Mi"},
        "Gold": {"cpu": "3000m", "memory": "3072Mi"},
        "Platinum": {"cpu": "4000m", "memory": "4096Mi"},
    }

    def get_config(self):
        return {
            "env.rpcuser": self.config.chart_config.rpcuser,
            "env.rpcpasswd": self.config.chart_config.rpcpassword,
            "global.ingress.host": self.config.chart_config.domain,
        }

    def _check_uniqueness(self):
        if get_deployments(self.SOLUTION_TYPE, self.config.username):
            raise StopChatFlow("You can only have one Digibyte solution per VDC")

    def get_release_name(self):
        self._check_uniqueness()
        super().get_release_name()

    def _enter_credentials(self):

        form = self.new_form()
        rpcuser = form.string_ask("RPC Username", required=True)
        rpcpassword = form.secret_ask("RPC Password", required=True)
        form.ask()
        self.config.chart_config.rpcuser = rpcuser.value
        self.config.chart_config.rpcpassword = rpcpassword.value

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._enter_credentials()
        self.vdc.get_deployer().kubernetes.add_traefik_entrypoints(
            {"digibyte-p2p": {"port": "12024"}, "digibyte-rpc": {"port": "14022"}}
        )


chat = DigibyteDeploy
