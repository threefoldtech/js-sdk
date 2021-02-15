from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class PresearchDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "presearch"
    title = "Presearch"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    CHART_LIMITS = {
        "Silver": {"cpu": "2000m", "memory": "2024Mi"},
        "Gold": {"cpu": "3000m", "memory": "3072Mi"},
        "Platinum": {"cpu": "4000m", "memory": "4096Mi"},
    }

    def _check_uniqueness(self):
        username = self.user_info()["username"]
        self.md_show_update("Preparing the chatflow...")
        if get_deployments(self.SOLUTION_TYPE, username):
            raise StopChatFlow("You can only have one Presearch solution per VDC")

    def get_release_name(self):
        self._check_uniqueness()
        super().get_release_name()

    def _enter_registration_code(self):

        form = self.new_form()
        self.registration_code = form.string_ask("Enter Registration Code", required=True)
        form.ask()
        self.registration_code = self.registration_code.value

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._enter_registration_code()
        self._choose_flavor(self.CHART_LIMITS)

        self.chart_config.update(
            {
                "REGISTRATION_CODE": self.registration_code,
                "global.ingress.host": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )

chat = PresearchDeploy
