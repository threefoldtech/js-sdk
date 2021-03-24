from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
import json


class FileBrowser(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "filebrowser"
    title = "File Browser"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "get_release_name",
        "choose_flavor",
        "create_subdomain",
        "get_documentserver_value",
        "set_config",
        "install_chart",
        "initializing",
        "success",
    ]

    @chatflow_step(title="Document server URL")
    def get_documentserver_value(self):
        message = "Please enter Document Server URL"
        self.document_server_url = self.string_ask(message, required=True, md=True)

    @chatflow_step(title="Configurations")
    def set_config(self):
        self.chart_config.update(
            {
                "extraEnvVars[0].name": "DOCUMENTSERVER_URL",
                "extraEnvVars[0].value": self.document_server_url,
                "ingress.hosts[0]": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )


chat = FileBrowser
