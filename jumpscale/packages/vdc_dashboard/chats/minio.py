from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class MinioDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "minio"
    title = "Quantum Storage"
    HELM_REPO_NAME = "marketplace"
    steps = [
        "get_release_name",
        "create_subdomain",
        "set_config",
        "quantum_storage" "install_chart",
        "initializing",
        "success",
    ]

    @chatflow_step(title="Configurations")
    def set_config(self):
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

        self.chart_config.update({"ingress.host": self.domain, "accessKey": accesskey.value, "secretKey": secret.value})

    @chatflow_step(title="Quantum Storage")
    def quantum_storage(self):
        self.md_show_update("Initializing Quantum Storage, This may take few seconds ...")
        path = "/home/rancher/minio"
        qs = self.vdc.get_quantumstorage_manager()
        qs.apply(path)


chat = MinioDeploy
