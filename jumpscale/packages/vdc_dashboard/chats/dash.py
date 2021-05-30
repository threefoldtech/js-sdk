from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class DashDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "dash"
    title = "Dash"
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
        "Gold": {"cpu": "2000m", "memory": "4000Mi"},
        "Platinum": {"cpu": "4000m", "memory": "8000Mi"},
    }

    def get_config(self):
        return {
            "env.rpcuser": self.config.chart_config.rpcuser,
            "env.rpcpasswd": self.config.chart_config.rpcpassword,
            "env.node_ingress_ip": self.vdc_info["public_ip"],
            "global.ingress.host": self.config.chart_config.domain,
        }

    def _check_uniqueness(self):
        if get_deployments(self.SOLUTION_TYPE, self.config.username):
            raise StopChatFlow("You can only have one Dash solution per VDC")

    @chatflow_step(title="Solution Name")
    def get_release_name(self):
        self._check_uniqueness()
        message = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
        releases = [
            release["name"]
            for release in self.k8s_client.list_deployed_releases()
            if release["namespace"].startswith(self.chart_name)
        ]
        self.config.release_name = self.string_ask(
            message, required=True, is_identifier=True, not_exist=["solution name", releases], md=True, max_length=10
        )

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
            {"dash-p2p": {"port": "9999"}, "dash-rpc": {"port": "9998"}}
        )


chat = DashDeploy
