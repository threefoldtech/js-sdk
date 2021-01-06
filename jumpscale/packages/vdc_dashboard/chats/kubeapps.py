from textwrap import dedent
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.packages.vdc_dashboard.sals.solutions_chatflow import SolutionsChatflowDeploy
import json


class KubeappsDeploy(SolutionsChatflowDeploy):
    SOLUTION_TYPE = "kubeapps"
    title = "Kubeapps"
    HELM_REPO_NAME = "marketplace"
    steps = ["get_release_name", "create_subdomain", "set_config", "install_chart", "initializing", "get_access_token","success"]
    access_token= None
    @chatflow_step(title="Configurations")
    def set_config(self):
        self._choose_flavor()

        self.chart_config.update({
            "ingress.hostname": self.domain,
            "kubeops.resources.limits.cpu": self.resources_limits["cpu"],
            "kubeops.resources.limits.memory": self.resources_limits["memory"],
         })

    def get_specific_service(self,all_services,service_name):
        service_account = [service_account['metadata']['name'] for service_account in all_services['items'] if service_account['metadata']['name'] == service_name] 
        if service_account:
            return True
        
        return False

    @chatflow_step(title="Generating access token")
    def get_access_token(self):
        self._get_vdc_info()
        # Validate service account 
        services=self.k8s_client.execute_native_cmd("kubectl get serviceaccount -o json")
        all_service_account = json.loads(services)
        if not self.get_specific_service(all_service_account, "kubeapps-operator"):
            self.k8s_client.execute_native_cmd(
                cmd="kubectl create serviceaccount kubeapps-operator"
            )

        # Validate clusterrolebinding
        services=self.k8s_client.execute_native_cmd("kubectl get clusterrolebinding -o json")
        all_cluster_rolebinding = json.loads(services)

        if not self.get_specific_service(all_cluster_rolebinding, "kubeapps-operator"):
            self.k8s_client.execute_native_cmd(
                cmd="kubectl create clusterrolebinding kubeapps-operator --clusterrole=cluster-admin --serviceaccount=default:kubeapps-operator"
            )

        try:
            cmd = r"""kubectl get secret $(kubectl get serviceaccount kubeapps-operator -o jsonpath='{range .secrets[*]}{.name}{"\n"}{end}' | grep kubeapps-operator-token) -o jsonpath='{.data.token}' -o go-template='{{.data.token | base64decode}}'"""
            self.access_token = self.k8s_client.execute_native_cmd(
                cmd = cmd
            )
        except Exception as ex:
            raise StopChatFlow(
                "There is an issue happened during getting access token to be able to access kubeapps solution"
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
