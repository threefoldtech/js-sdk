from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class PresearchDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "presearch"
    title = "Presearch"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    CHART_LIMITS = {
        "Silver": {"cpu": "400m", "memory": "300Mi"},
        "Gold": {"cpu": "600m", "memory": "500Mi"},
    }

    def _check_uniqueness(self):
        username = self.user_info()["username"]
        self.md_show_update("Preparing the Chatflow . . .")
        if get_deployments(self.SOLUTION_TYPE, username):
            raise StopChatFlow("You can only have one Presearch solution per VDC")

    def get_release_name(self):
        self._check_uniqueness()
        super().get_release_name()
        if len(self.release_name) > 10:
            raise StopChatFlow("Solution Name should not be more than 10 characters")

    def _enter_registration_code(self):
        self.registration_code = self.string_ask("Enter Registration Code", required=True)

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._enter_registration_code()
        self._choose_flavor(self.CHART_LIMITS)

        self.chart_config.update(
            {
                "registration_code": self.registration_code,
                "global.ingress.host": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = PresearchDeploy
