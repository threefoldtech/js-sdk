from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy


class KubeappsDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "kubeapps"
    title = "Kubeapps"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "generate_access_token","success"]
    access_token= None
    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()

        self.chart_config = {
            "ingress.hostname": self.domain,
         }

    @chatflow_step(title="Generating access token")
    def generate_access_token(self):
        self._get_vdc_info()
        self.access_token = self.k8s_client.execute_native_cmd(
            cmd=f"kubectl get secret $(kubectl get serviceaccount kubeapps-operator -o jsonpath='{range .secrets[*]}{.name}{"\n"}{end}' | grep kubeapps-operator-token) -o jsonpath='{.data.token}' -o go-template='{{.data.token | base64decode}}'"
        )
        if not self.access_token :
            raise StopChatFlow(
                "There is an issue happened during getting access token to be able to access kubeapps solution"
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        extra_info = f'The access token will be used to login is {self.access_token}'
        super().success(extra_info=extra_info)

chat = KubeappsDeploy
