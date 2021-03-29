from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
import json


class FileBrowser(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "filebrowser"
    title = "File Browser"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "create_subdomain",
        "get_documentserver_value",
        "install_chart",
        "initializing",
        "success",
    ]

    def get_config(self):
        return {
            "extraEnvVars[0].name": "DOCUMENTSERVER_URL",
            "extraEnvVars[0].value": self.config.chart_config.document_server_url,
            "ingress.hosts[0]": self.config.chart_config.domain,
        }

    @chatflow_step(title="Document server URL")
    def get_documentserver_value(self):
        message = "Please enter Document Server URL"
        self.config.chart_config.document_server_url = self.string_ask(message, required=True, md=True)


chat = FileBrowser
