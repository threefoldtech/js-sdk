from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
import binascii
from jumpscale.loader import j


class MastodonDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "mastodon"
    title = "Mastodon"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "success"]

    def _configure_admin_username_email(self):
        valid_password = False
        while not valid_password:
            form = self.new_form()
            admin_email_message = "Admin email (The password will be generated randomly. Reset it once the site is up.)"
            admin_user_message = "Admin Username"
            admin_email = form.string_ask(admin_email_message, required=True, is_identifier=True)
            admin_username = form.string_ask(admin_user_message, required=True, is_identifier=True)
            form.ask()
            self.admin_email = admin_email.value
            self.admin_username = admin_username.value

    def _generate_secrets(self):
        self.secret_key_base = binascii.hexlify(j.data.idgenerator.nbytes(64)).decode()
        self.otp_secret = binascii.hexlify(j.data.idgenerator.nbytes(64)).decode()
        self.vapid_public = binascii.hexlify(j.data.idgenerator.nbytes(64)).decode()
        self.vapid_private = binascii.hexlify(j.data.idgenerator.nbytes(64)).decode()

    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()
        self._configure_admin_username_email()
        self._ask_smtp_settings()

        self.chart_config.update(
            {
                "ingress.hostname": self.domain,
                "secrets.secret_key_base": self.secret_key_base,
                "secrets.otp_secret": self.otp_secret,
                "secrets.vapid.private_key": self.vapid_private,
                "secrets.vapid.public_key": self.vapid_public,
                "smtp.from_address": self.smtp_username,
                "smtp.login": self.smtp_username,
                "smtp.password": self.smtp_password,
                "smtp.server": self.smtp_host,
                "smtp.port": self.smtp_port,
                "createAdmin.username": self.admin_username,
                "createAdmin.email": self.admin_email,
            }
        )

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        super().initializing(timeout=1200)


chat = MastodonDeploy
