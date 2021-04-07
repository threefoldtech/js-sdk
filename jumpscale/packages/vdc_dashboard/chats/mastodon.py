from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class MastodonDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "mastodon"
    title = "Mastodon"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    @chatflow_step(title="Configurations")
    def set_config(self):

        self._choose_flavor()
        self._ask_smtp_settings()
        self.chart_config.update(
            {
                "web.ingress.host": self.domain,
                "resources.limits.cpu": self.resources_limits["cpu"],
                "resources.limits.memory": self.resources_limits["memory"],
                "env.smtp.server": self.smtp_host,
                "env.smtp.port": self.smtp_port.strip('"'),
                "env.smtp.address": self.smtp_host,
                "env.smtp.login": self.smtp_username,
                "env.smtp.domain": self.domain,
            }
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        extra_info = f"Admin user credentials for owncloud is: \
    <br/> Username: admin<br/> Password: password<br/>Mariadb rootpassword: secretpassword<br/>Please consider changing them after login"
        super().success(extra_info=extra_info)


chat = MastodonDeploy
