from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
import json


class DocumentServer(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "documentserver"
    title = "Document Server"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "create_subdomain",
        "install_chart",
        "initializing",
        "success",
    ]

    def get_config(self):
        return {
            "ingress.hosts[0]": self.config.chart_config.domain,
        }


chat = DocumentServer
