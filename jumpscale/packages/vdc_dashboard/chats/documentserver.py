from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
import json


class DocumentServer(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "documentserver"
    title = "Document Server"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "get_release_name",
        "choose_flavor",
        "create_subdomain",
        "set_config",
        "install_chart",
        "initializing",
        "success",
    ]

    @chatflow_step(title="Configurations")
    def set_config(self):
        self.chart_config.update(
            {
                "ingress.hosts[0]": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = DocumentServer
