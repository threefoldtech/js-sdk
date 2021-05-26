import re
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class MastodonDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "mastodon"
    title = "Mastodon"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "init_chatflow",
        "get_release_name",
        "choose_flavor",
        "set_config",
        "create_subdomain",
        "get_admin_data",
        "install_chart",
        "initializing",
        "success",
    ]
    CHART_LIMITS = {
        "Silver": {"cpu": "3000m", "memory": "3072Mi"},
        "Gold": {"cpu": "4000m", "memory": "4096Mi"},
        "Platinum": {"cpu": "5000m", "memory": "5120Mi"},
    }

    def get_config(self):
        return {
            "web.ingress.host": self.config.chart_config.domain,
            "resources.limits.cpu": self.config.chart_config.resources_limits["cpu"][:-1],
            "resources.limits.memory": self.config.chart_config.resources_limits["memory"][:-2],
        }

    def get_config_string_safe(self):
        return {
            "env.smtp.server": self.config.chart_config.smtp_host,
            "env.smtp.port": self.config.chart_config.smtp_port,
            "env.smtp.address": f"support@{self.config.chart_config.domain}",
            "env.smtp.login": self.config.chart_config.smtp_username,
            "env.smtp.domain": self.config.chart_config.domain,
            "smtpPassword": self.config.chart_config.smtp_password,
            "env.extraEnvVars[0].name": "THREEBOT_KEY",
            "env.extraEnvVars[0].value": self.generate_signing_key(),
        }

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._ask_smtp_settings()

    @chatflow_step(title="Admin Data")
    def get_admin_data(self):
        form = self.new_form()
        reserved_names = ["admin", "support", "help", "root", "webmaster", "administrator", "mod", "moderator"]
        admin_name = form.string_ask(
            "Please add admin username", required=True, is_identifier=True, not_allowed=["admin user", reserved_names]
        )
        admin_email = form.string_ask("Please add the admin email", required=True, md=True)
        form.ask()
        self.config.chart_config.admin_name = admin_name.value
        self.config.chart_config.admin_email = admin_email.value

    def create_admin_account(self):
        pod_name = self.get_pods("web")[0]
        command = f"bin/tootctl accounts create {self.config.chart_config.admin_name} --email {self.config.chart_config.admin_email} --confirmed --role admin"
        result = self.exec_command_in_pod(pod_name=pod_name, command=command)
        return result.splitlines()[-1].split(" ")[-1]

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        password = self.create_admin_account()
        extra_info = f"Admin user credentials for mastodon is: \
    <br/> Admin Email:{self.config.chart_config.admin_email} <br/> Admin Password: {password}"
        super().success(extra_info=extra_info)


chat = MastodonDeploy
