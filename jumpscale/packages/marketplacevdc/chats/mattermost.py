from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.marketplacevdc.sals.solutions_chatflow import SolutionsChatflowDeploy


class MattermostDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "mattermost"
    title = "Mattermost"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "select_vdc",
        "get_release_name",
        "create_subdomain",
        "set_config",
        "install_chart",
        "success",
    ]

    @chatflow_step(title="Configurations")
    def set_config(self):

        form = self.new_form()
        mysql_user = form.string_ask("Enter mysql user name", default="mysql", min_length=3, required=True,)
        mysql_password = form.secret_ask(
            "Enter mysql password", default="mySqlPassword", min_length=8, required=True,
        )  # TODO: need to check a valid password
        mysql_root_password = form.secret_ask(
            "Enter mysql password for root user", default="mySqlRootPassword", min_length=8, required=True,
        )  # TODO: need to check a valid password
        form.ask()

        self._choose_flavor()
        self.chart_config = {
            "ingress.host": self.domain,
            "mysql.mysqlUser": mysql_user.value,
            "mysql.mysqlPassword": mysql_password.value,
            "mysql.mysqlRootPassword": mysql_root_password.value,
            "resources.limits.cpu": self.resources_limits["cpu"],
            "resources.limits.memory": self.resources_limits["memory"],
        }


chat = MattermostDeploy
