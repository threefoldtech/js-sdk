from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class KubeappsDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "kubeapps"
    title = "Kubeapps"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()

        self.chart_config = {
            "ingress.hostname": self.domain,
         }

chat = KubeappsDeploy
