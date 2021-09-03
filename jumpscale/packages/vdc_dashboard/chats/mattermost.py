from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class MattermostDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "mattermost"
    title = "Mattermost"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "set_config",
        "create_subdomain",
        "install_chart",
        "initializing",
        "success",
    ]
    ADDITIONAL_QUERIES = [
        {"cpu": 100, "memory": 256},  # mysql
        {"cpu": 10, "memory": 10},  # initContainer.remove-lost-found
    ]

    def get_config(self):
        return {
            "ingress.host": self.config.chart_config.domain,
            "mysql.mysqlUser": self.config.chart_config.mysql_user,
            "mysql.mysqlPassword": self.config.chart_config.mysql_password,
            "mysql.mysqlRootPassword": self.config.chart_config.mysql_root_password,
        }

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

        self.config.chart_config.mysql_user = mysql_user.value
        self.config.chart_config.mysql_password = mysql_password.value
        self.config.chart_config.mysql_root_password = mysql_root_password.value


chat = MattermostDeploy
