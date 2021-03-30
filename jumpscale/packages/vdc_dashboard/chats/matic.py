from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class MaticDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "matic"
    title = "Polygon (Matic)"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    CHART_LIMITS = {
        "Silver": {"cpu": "2000m", "memory": "2024Mi"},
        "Gold": {"cpu": "4000m", "memory": "4096Mi"},
        "Platinum": {"cpu": "4000m", "memory": "8192Mi"},
    }

    def _enter_nodetype(self):
        choices = [
            "Sentry Node",
            "Full Node",
            "Validator",
        ]
        self.node_type = self.single_choice("Select the Node Type", choices, default="Sentry Node")
        if self.node_type == "Full Node":
            self._enter_rpc_url()
        elif self.node_type == "Validator":
            self._enter_rpc_url()
            self._enter_validator_info()
            self._enter_sentry_info()
        else:
            pass

        self.chart_config.update({"env.node_type": self.node_type})

    def _check_uniqueness(self):
        username = self.user_info()["username"]
        self.md_show_update("Preparing the chatflow . .")
        if get_deployments(self.SOLUTION_TYPE, username):
            raise StopChatFlow("You can only have one Matic solution per VDC")

    def get_release_name(self):
        self._check_uniqueness()
        super().get_release_name()
        if len(self.release_name) > 10:
            raise StopChatFlow("Solution Name should not be more than 10 characters")

    def _enter_access_code(self):
        self.access_code = self.secret_ask(
            "Enter Access Code (This would be used to access your node's web page)", min_length=8, required=True
        )

    def _enter_rpc_url(self):
        self.eth_rpc_url = self.string_ask("Insert Infura or any full node RPC URL to Ethereum.", required=True,)
        self.chart_config.update({"env.eth_rpc_url": self.eth_rpc_url})

    def _enter_validator_info(self):
        form = self.new_form()
        self.eth_privkey = form.string_ask("Please enter your ethereum wallet's *private* key.", required=True)
        self.eth_key_passphrase = form.secret_ask(
            "Please enter the passphrase for your ethereum wallet's *private* key. It should be minimum 8 characters.",
            min_length=8,
            required=True,
        )
        self.eth_walletaddr = form.string_ask("Please enter your ethereum wallet address.", required=True)
        form.ask()
        self.eth_privkey = self.eth_privkey.value
        self.eth_key_passphrase = self.eth_key_passphrase.value
        self.eth_walletaddr = self.eth_walletaddr.value
        self.chart_config.update(
            {
                "eth_privkey": self.eth_privkey,
                "eth_key_passphrase": self.eth_key_passphrase,
                "env.eth_walletaddr": self.eth_walletaddr,
            }
        )

    def _enter_sentry_info(self):
        form = self.new_form()
        self.sentry_nodeid = form.string_ask("Please enter your sentry node's NodeID for heimdall")
        self.sentry_enodeid = form.string_ask("Please enter your sentry node's EnodeID for Bor")
        form.ask()
        self.sentry_nodeid = self.sentry_nodeid.value
        self.sentry_enodeid = self.sentry_enodeid.value
        self.chart_config.update({"env.sentry_nodeid": self.sentry_nodeid, "env.sentry_enodeid": self.sentry_enodeid})

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._enter_nodetype()
        self._enter_access_code()
        self._choose_flavor(self.CHART_LIMITS)
        self.vdc.get_deployer().kubernetes.add_traefik_entrypoints(
            {"matic-bor": {"port": "30303"}, "matic-heimdall": {"port": "26656"}}
        )

        self.chart_config.update(
            {
                "access_code": self.access_code,
                "global.ingress.host": self.domain,
                "env.moniker": self.release_name,
                "env.node_ingress_ip": self.vdc_info["public_ip"],
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = MaticDeploy
