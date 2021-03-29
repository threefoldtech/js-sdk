from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_deployments


class PresearchDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "presearch"
    title = "Presearch"
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
        "Silver": {"cpu": "400m", "memory": "300Mi"},
        "Gold": {"cpu": "600m", "memory": "500Mi"},
    }

    def get_config(self):
        return {
            "registration_code": self.config.chart_config.registration_code,
            "global.ingress.host": self.config.chart_config.domain,
        }

    def _check_uniqueness(self):
        if get_deployments(self.SOLUTION_TYPE, self.config.username):
            raise StopChatFlow("You can only have one Presearch solution per VDC")

    def get_release_name(self):
        self._check_uniqueness()
        super().get_release_name()

    def _enter_registration_code(self):
        self.config.chart_config.registration_code = self.string_ask("Enter Registration Code", required=True)

    @chatflow_step(title="Node Configuration")
    def set_config(self):
        self._enter_registration_code()


chat = PresearchDeploy
