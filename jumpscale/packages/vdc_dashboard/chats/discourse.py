from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class DiscourseDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "discourse"
    title = "Discourse"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]
    ADDITIONAL_QUERIES = [{"cpu": 250, "memory": 256}]  # postgres

    def _configure_admin_username_password(self):
        valid_password = False
        while not valid_password:
            form = self.new_form()
            admin_user_message = "Admin username"
            admin_pass_message = "Admin Password (should be at least 10 characters long, Shouldn't include username)"
            admin_username = form.string_ask(admin_user_message, required=True, is_identifier=True)
            admin_password = form.secret_ask(admin_pass_message, required=True, is_identifier=True, min_length=10)
            form.ask()
            self.admin_username = admin_username.value
            self.admin_password = admin_password.value
            if self.admin_username in self.admin_password:
                self.md_show("Invalid password, shouldn't include username, Please try again")
            else:
                valid_password = True

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()
        self._configure_admin_username_password()
        self._ask_smtp_settings()

        self.chart_config.update(
            {
                "discourse.host": self.domain,
                "discourse.siteName": self.release_name,
                "discourse.username": self.admin_username,
                "discourse.password": self.admin_password,
                "ingress.hostname": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
                "discourse.extraEnvVars[0].name": "SMTP_HOST",
                "discourse.extraEnvVars[0].value": self.smtp_host,
                "discourse.extraEnvVars[1].name": "SMTP_PORT",
                "discourse.extraEnvVars[1].value": self.smtp_port,
                "discourse.extraEnvVars[2].name": "SMTP_USER",
                "discourse.extraEnvVars[2].value": self.smtp_username,
                "discourse.extraEnvVars[3].name": "SMTP_PASSWORD",
                "discourse.extraEnvVars[3].value": self.smtp_password,
                "discourse.extraEnvVars[3].name": "THREEBOT_KEY",
                "discourse.extraEnvVars[3].value": self.generate_signing_key(),
                "sidekiq.extraEnvVars[0].name": "SMTP_HOST",
                "sidekiq.extraEnvVars[0].value": self.smtp_host,
                "sidekiq.extraEnvVars[1].name": "SMTP_PORT",
                "sidekiq.extraEnvVars[1].value": self.smtp_port,
                "sidekiq.extraEnvVars[2].name": "SMTP_USER",
                "sidekiq.extraEnvVars[2].value": self.smtp_username,
                "sidekiq.extraEnvVars[3].name": "SMTP_PASSWORD",
                "sidekiq.extraEnvVars[3].value": self.smtp_password,
            }
        )

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        super().initializing(timeout=1200)


chat = DiscourseDeploy
