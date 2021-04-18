from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class DiscourseDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "discourse"
    title = "Discourse"
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
    ADDITIONAL_QUERIES = [{"cpu": 250, "memory": 256}]  # postgres

    def get_config(self):
        return {
            "discourse.host": self.config.chart_config.domain,
            "discourse.siteName": self.config.release_name,
            "discourse.username": self.config.chart_config.admin_username,
            "discourse.password": self.config.chart_config.admin_password,
            "ingress.hostname": self.config.chart_config.domain,
        }

    def get_config_string_safe(self):
        return {
            "discourse.extraEnvVars[0].name": "SMTP_HOST",
            "discourse.extraEnvVars[0].value": self.config.chart_config.smtp_host,
            "discourse.extraEnvVars[1].name": "SMTP_PORT",
            "discourse.extraEnvVars[1].value": self.config.chart_config.smtp_port,
            "discourse.extraEnvVars[2].name": "SMTP_USER",
            "discourse.extraEnvVars[2].value": self.config.chart_config.smtp_username,
            "discourse.extraEnvVars[3].name": "SMTP_PASSWORD",
            "discourse.extraEnvVars[3].value": self.config.chart_config.smtp_password,
            "discourse.extraEnvVars[4].name": "THREEBOT_KEY",
            "discourse.extraEnvVars[4].value": self.generate_signing_key(),
            "sidekiq.extraEnvVars[0].name": "SMTP_HOST",
            "sidekiq.extraEnvVars[0].value": self.config.chart_config.smtp_host,
            "sidekiq.extraEnvVars[1].name": "SMTP_PORT",
            "sidekiq.extraEnvVars[1].value": self.config.chart_config.smtp_port,
            "sidekiq.extraEnvVars[2].name": "SMTP_USER",
            "sidekiq.extraEnvVars[2].value": self.config.chart_config.smtp_username,
            "sidekiq.extraEnvVars[3].name": "SMTP_PASSWORD",
            "sidekiq.extraEnvVars[3].value": self.config.chart_config.smtp_password,
        }

    def _configure_admin_username_password(self):
        valid_password = False
        while not valid_password:
            form = self.new_form()
            admin_user_message = "Admin username"
            admin_pass_message = "Admin Password (should be at least 10 characters long, Shouldn't include username)"
            admin_username = form.string_ask(admin_user_message, required=True, is_identifier=True)
            admin_password = form.secret_ask(admin_pass_message, required=True, is_identifier=True, min_length=10)
            form.ask()
            self.config.chart_config.admin_username = admin_username.value
            self.config.chart_config.admin_password = admin_password.value
            if self.config.chart_config.admin_username in self.config.chart_config.admin_password:
                self.md_show("Invalid password, shouldn't include username, Please try again")
            else:
                valid_password = True

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._configure_admin_username_password()
        self._ask_smtp_settings()


chat = DiscourseDeploy
