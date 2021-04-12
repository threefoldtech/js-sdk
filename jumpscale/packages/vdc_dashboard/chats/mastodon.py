import re
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class MastodonDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "mastodon"
    title = "Mastodon"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "get_release_name",
        "create_subdomain",
        "set_config",
        "get_admin_data",
        "install_chart",
        "initializing",
        "success",
    ]
    CHART_LIMITS = {
        "Silver": {"cpu": "3000m", "memory": "3024Mi"},
        "Gold": {"cpu": "4000m", "memory": "4096Mi"},
        "Platinum": {"cpu": "5000m", "memory": "5120Mi"},
    }

    @chatflow_step(title="Configurations")
    def set_config(self):

        self._choose_flavor(chart_limits=self.CHART_LIMITS)
        self._ask_smtp_settings()
        self.chart_config.update(
            {
                "web.ingress.host": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"][:-1],
                "resources.limits.memory": self.resources_limits["memory"][:-2],
                "env.smtp.server": self.smtp_host,
                "env.smtp.port": self.smtp_port.strip('"'),
                "env.smtp.address": f"support@{self.domain}",
                "env.smtp.login": self.smtp_username,
                "env.smtp.domain": self.domain,
                "smtpPassword": self.smtp_password,
                "env.extraEnvVars[0].name": "THREEBOT_KEY",
                "env.extraEnvVars[0].value": self.generate_signing_key(),
            }
        )

    @chatflow_step(title="Admin Data")
    def get_admin_data(self):
        form = self.new_form()
        admin_name = form.string_ask("Please add admin username", required=True, is_identifier=True)
        admin_email = form.string_ask("Please add the admin email", required=True, md=True)
        form.ask()
        self.admin_name = admin_name.value
        self.admin_email = admin_email.value

    def create_admin_account(self):
        pod_name = self.get_pods("web")[0]
        command = f"bin/tootctl accounts create {self.admin_name} --email {self.admin_email} --confirmed --role admin"
        result = self.exec_command_in_pod(pod_name=pod_name, command=command)
        return result.splitlines()[-1].split(" ")[-1]

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        password = self.create_admin_account()
        extra_info = f"Admin user credentials for mastodon is: \
    <br/> Admin Email:{self.admin_email} <br/> Admin Password: {password}"
        super().success(extra_info=extra_info)


chat = MastodonDeploy
