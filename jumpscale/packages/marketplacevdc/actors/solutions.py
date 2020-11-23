from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method

# from shlex import quote
# from kubernetes import client, config


class Solutions(BaseActor):
    def _list_all_solutions(self) -> str:
        """List all deployments from kubectl and corresponding helm list info

        """
        all_deployments = []
        # for vdc in all_vdcs:
        # TODO loop over all vdc instances and get config path
        vdc_info = {}  # TODO to be removed
        vdc_info["kube_config_path"] = f"{j.core.dirs.HOMEDIR}/.kube/config"  # TODO to be removed
        k8s_client = j.sals.kubernetes.Manager(config_path=vdc_info["kube_config_path"])

        # Get all deployments
        kubectl_deployment_info = k8s_client.execute_native_cmd(cmd=f"kubectl get deployments -o json")
        deployments = j.data.serializers.json.loads(kubectl_deployment_info)["items"]

        for deployment_info in deployments:
            release_name = deployment_info["metadata"]["labels"]["app.kubernetes.io/instance"]
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)

            deployment_info.update({"userSuppliedValues": j.data.serializers.json.loads(helm_chart_supplied_values)})
            all_deployments.append(deployment_info)

        return all_deployments

    def _list_solutions(self, solution_type: str = None) -> str:
        """
        List deployments for specific solution type selected from kubectl and corresponding helm list info

        """
        all_deployments = []
        # for vdc in all_vdcs:
        # TODO loop over all vdc instances and get config path
        vdc_info = {}  # TODO to be removed
        vdc_info["kube_config_path"] = f"{j.core.dirs.HOMEDIR}/.kube/config"  # TODO to be removed
        k8s_client = j.sals.kubernetes.Manager(config_path=vdc_info["kube_config_path"])
        # Get deployments for specific solution type in k8s cluster
        # returns a json string
        kubectl_deployment_info = k8s_client.execute_native_cmd(
            cmd=f'kubectl get deployments -o=jsonpath=\'{{range .items[?(@.metadata.labels.app\.kubernetes\.io/name=="{solution_type}")]}}{{@}}{{"\\n"}}{{end}}\''
        )
        # TODO Improve splitting
        deployments = kubectl_deployment_info.split("\n")[:-1]

        for deployment_json_str in deployments:
            deployment_info = j.data.serializers.json.loads(deployment_json_str)
            release_name = deployment_info["metadata"]["labels"]["app.kubernetes.io/instance"]
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)

            deployment_info.update({"userSuppliedValues": j.data.serializers.json.loads(helm_chart_supplied_values)})
            all_deployments.append(deployment_info)

        return all_deployments

    @actor_method
    def list_solutions(self, solution_type: str = None) -> str:
        if solution_type:
            deployments = self._list_solutions(solution_type=solution_type)
        else:
            deployments = self._list_all_solutions()

        return j.data.serializers.json.dumps(deployments)


Actor = Solutions
