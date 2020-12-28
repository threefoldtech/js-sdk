from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class DiscourseDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "discourse"
    title = "Discourse"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()
        self._configure_admin_username_password()

        self.chart_config = {
            "discourse.host": self.domain,
            "discourse.siteName": self.release_name,
            "discourse.username": self.admin_username.value,
            "discourse.password": self.admin_password.value,
            "ingress.hostname": self.domain,
            "resources.limits.cpu": self.resources_limits["cpu"],
            "resources.limits.memory": self.resources_limits["memory"],
        }
        # subdomain selected on gateway on preferred farm
        if self.preferred_farm_gw:
            self.chart_config.update({"ingress.certresolver": "ghanem"})

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        super().initializing(timeout=1200)


chat = DiscourseDeploy
