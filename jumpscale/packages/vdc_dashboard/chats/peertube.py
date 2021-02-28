from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class PeertubeDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "peertube"
    title = "Peertube"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]
    ADDITIONAL_QUERIES = [{"cpu": 250, "memory": 256}]  # postgres

    def _get_smtp(self):
        form = self.new_form()
        self.email_username = form.string_ask("Please add the host e-mail address for your solution", required=True)
        self.email_host = form.string_ask(
            "Please add the smtp host example: `smtp.gmail.com`", default="smtp.gmail.com", required=True, md=True
        )
        self.email_password = form.secret_ask("Please add the host e-mail password", required=True)

        form.ask()
        self.email_username = self.email_username.value
        self.email_host = self.email_host.value
        self.email_password = self.email_password.value

        self.email_from = self.email_username
        self.admin_email = self.email_username

    @chatflow_step(title="Configurations")
    def set_config(self):
        user_info = self.user_info()
        self.user_email = user_info["email"]

        self._choose_flavor()
        self.chart_config.update(
            {
                "webserver.hostname": self.domain,
                "postgresql.fullnameOverride": f"peertube-postgresql-{self.release_name}",
                "redis.fullnameOverride": f"peertube-redis-{self.release_name}",
                "deps.smtp.hostname": None,
                "deps.smtp.username": None,
                "deps.smtp.password": None,
                "deps.smtp.from": None,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
            }
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        extra_info = f"Admin user credentials for peertube is: <br/> Email: adminemail@gmail.com <br/> Password: adminPassword <br/> Please consider changing them after login"
        super().success(extra_info=extra_info)


chat = PeertubeDeploy
