from textwrap import dedent
from time import time

import gevent
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.loader import j

POD_INITIALIZING_TIMEOUT = 120


class MinioDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "minio"
    title = "Minio Quantum Storage"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "init_chatflow",
        "get_release_name",
        "set_config",
        "create_subdomain",
        "quantum_storage",
        "install_chart",
        "initializing",
        "success",
    ]

    def get_config(self):
        self.config.chart_config.resources_limits["cpu"] = "512m"
        self.config.chart_config.resources_limits["memory"] = "1Gi"
        return {
            "ingress.host": self.config.chart_config.domain,
            "accessKey": self.config.chart_config.accesskey,
            "secretKey": self.config.chart_config.secret,
            "volume.hostPath": self.config.chart_config.path,
            "resources.limits.cpu": self.config.chart_config.resources_limits["cpu"],
            "resources.limits.memory": self.config.chart_config.resources_limits["memory"],
        }

    @chatflow_step(title="Configurations")
    def set_config(self):
        self.config.chart_config.path = f"/home/rancher/{self.chart_name}{self.config.release_name}"

        form = self.new_form()
        accesskey = form.string_ask(
            "Please add the key to be used for minio when logging in. Make sure not to lose it",
            min_length=3,
            required=True,
        )
        secret = form.secret_ask(
            "Please add the secret to be used for minio when logging in to match the previous key. Make sure not to lose it",
            min_length=8,
            required=True,
        )
        form.ask()
        self.config.chart_config.accesskey = accesskey.value
        self.config.chart_config.secret = secret.value

    @chatflow_step(title="Quantum Storage")
    def quantum_storage(self):
        self.md_show_update("Initializing Quantum Storage, This may take few seconds ...")
        qs = self.vdc.get_quantumstorage_manager()
        qs.apply(self.config.chart_config.path)

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self, timeout=300):
        self.md_show_update(f"Initializing your {self.SOLUTION_TYPE}...")
        domain_message = ""
        if self.config.chart_config.domain:
            domain_message = f"Domain: {self.config.chart_config.domain}"
        error_message_template = f"""\
                Failed to initialize {self.SOLUTION_TYPE}, please contact support with this information:

                {domain_message}
                VDC Name: {self.vdc_name}
                Farm name: {self.vdc_info["farm_name"]}
                Reason: {{reason}}
                """
        start_time = time()
        while time() - start_time <= POD_INITIALIZING_TIMEOUT:
            if self.chart_pods_started():
                break
            gevent.sleep(1)

        if not self.chart_pods_started() and self.chart_resource_failure():
            stop_message = error_message_template.format(
                reason="Couldn't find resources in the cluster for the solution"
            )
            self.rollback()
            self.stop(dedent(stop_message))

        if self.config.chart_config.domain and not j.sals.reservation_chatflow.wait_http_test(
            f"https://{self.config.chart_config.domain}",
            timeout=timeout - POD_INITIALIZING_TIMEOUT,
            verify=False,
            status_code=403,
        ):
            stop_message = error_message_template.format(reason="Couldn't reach the website after deployment")
            self.rollback()
            self.stop(dedent(stop_message))
        self._label_resources(backupType="vdc")


chat = MinioDeploy
