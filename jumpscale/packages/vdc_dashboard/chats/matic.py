from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments, get_ingresstcp_used_ports


class MaticDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "matic"
    title = "Polygon (Matic)"
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
        "Gold": {"cpu": "4000m", "memory": "4096Mi"},
        "Platinum": {"cpu": "4000m", "memory": "8192Mi"},
    }

    def get_config(self):
        return {
            "access_code": self.config.chart_config.access_code,
            "global.ingress.host": self.config.chart_config.domain,
            "env.moniker": self.config.release_name,
            "env.node_ingress_ip": self.vdc_info["public_ip"],
            "env.node_type": self.config.chart_config.node_type,
            "env.eth_rpc_url": self.config.chart_config.extra_config.get("eth_rpc_url", ""),
            "eth_privkey": self.config.chart_config.extra_config.get("eth_privkey", ""),
            "eth_key_passphrase": self.config.chart_config.extra_config.get("eth_key_passphrase", ""),
            "env.eth_walletaddr": self.config.chart_config.extra_config.get("eth_walletaddr", ""),
            "env.sentry_nodeid": self.config.chart_config.extra_config.get("sentry_nodeid", ""),
            "env.sentry_enodeid": self.config.chart_config.extra_config.get("sentry_enodeid", ""),
        }

    def get_config_string_safe(self):
        return {
            "env.heimdall_svcp": str(self.config.chart_config.extra_config["heimdall_svcp"]),
            "env.bor_svcp": str(self.config.chart_config.extra_config["bor_svcp"]),
            "ports.heimdall": str(self.config.chart_config.extra_config["heimdall_svcp"]),
            "ports.bor": str(self.config.chart_config.extra_config["bor_svcp"]),
        }

    def _enter_nodetype(self):
        choices = [
            "Sentry Node",
            "Full Node",
            "Validator",
        ]
        self.config.chart_config.node_type = self.single_choice("Select the node type", choices, default="Sentry Node")
        if self.config.chart_config.node_type == "Full Node":
            self._enter_rpc_url()
        elif self.config.chart_config.node_type == "Validator":
            self._enter_rpc_url()
            self._enter_validator_info()
            self._enter_sentry_info()
        else:
            pass

    @chatflow_step(title="Solution Name")
    def get_release_name(self):
        message = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
        releases = [
            release["name"]
            for release in self.k8s_client.list_deployed_releases()
            if release["namespace"].startswith(self.chart_name)
        ]
        self.config.release_name = self.string_ask(
            message, required=True, is_identifier=True, not_exist=["solution name", releases], md=True, max_length=10
        )

    def _enter_rpc_url(self):
        self.config.chart_config.extra_config["eth_rpc_url"] = self.string_ask(
            "Insert Infura or any full node RPC URL to Ethereum.", required=True,
        )

    def _enter_validator_info(self):
        form = self.new_form()
        eth_privkey = form.string_ask("Please enter your ethereum wallet's *private* key.", required=True)
        eth_key_passphrase = form.secret_ask(
            "Please enter the passphrase for your ethereum wallet's *private* key. It should be minimum 8 characters.",
            min_length=8,
            required=True,
        )
        eth_walletaddr = form.string_ask("Please enter your ethereum wallet address.", required=True)
        form.ask()

        self.config.chart_config.extra_config["eth_privkey"] = eth_privkey.value
        self.config.chart_config.extra_config["eth_key_passphrase"] = eth_key_passphrase.value
        self.config.chart_config.extra_config["eth_walletaddr"] = eth_walletaddr.value

    def _enter_sentry_info(self):
        form = self.new_form()
        sentry_nodeid = form.string_ask("Please enter your sentry node's NodeID for heimdall")
        sentry_enodeid = form.string_ask("Please enter your sentry node's EnodeID for Bor")
        form.ask()

        self.config.chart_config.extra_config["sentry_nodeid"] = sentry_nodeid.value
        self.config.chart_config.extra_config["sentry_enodeid"] = sentry_enodeid.value

    @chatflow_step(title="Web Access")
    def _enter_access_code(self):
        self.config.chart_config.access_code = self.secret_ask(
            "Enter Access Code (This would be used to access your node's web page)", min_length=8, required=True
        )

    @chatflow_step(title="Port Settings")
    def _get_node_ports(self):
        usedports = get_ingresstcp_used_ports()
        msg = "For multiple deployments, please ensure to use different ports. TCP Ports already in use are " + str(
            usedports
        )
        form = self.new_form()
        heimdall_port = form.int_ask("Heimdall service port - default is 26656", default=26656, min=1000, max=65000)
        bor_port = form.int_ask("Bor service port - default is 30303", default=30303, min=1000, max=65000)
        form.ask(msg)

        valid = False
        error_msg = "Ports are already in use, please try ports other than " + str(usedports)
        while not valid:
            if heimdall_port.value in usedports or bor_port.value in usedports:
                form.ask(error_msg)
            else:
                valid = True

        self.config.chart_config.extra_config["heimdall_svcp"] = heimdall_port.value
        self.config.chart_config.extra_config["bor_svcp"] = bor_port.value

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._get_node_ports()
        self._enter_nodetype()
        self._enter_access_code()

        bor_entrypoint = "ingbor" + self.config.release_name
        heim_entrypoint = "ingheim" + self.config.release_name

        self.vdc.get_deployer().kubernetes.add_traefik_entrypoints(
            {
                bor_entrypoint: {"port": self.config.chart_config.extra_config["bor_svcp"]},
                heim_entrypoint: {"port": self.config.chart_config.extra_config["heimdall_svcp"]},
            }
        )


chat = MaticDeploy
