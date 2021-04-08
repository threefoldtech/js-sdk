from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class MastodonDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "mastodon"
    title = "Mastodon"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]
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
                "env.smtp.address": self.smtp_host,
                "env.smtp.login": self.smtp_username,
                "env.smtp.domain": self.domain,
                "env.extraEnvVars[0].name": "THREEBOT_KEY",
                "env.extraEnvVars[0].value": self.generate_signing_key(),
            }
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        extra_info = f"Admin user credentials for owncloud is: \
    <br/> Username: admin<br/> Password: password<br/>Mariadb rootpassword: secretpassword<br/>Please consider changing them after login"
        super().success(extra_info=extra_info)


chat = MastodonDeploy
