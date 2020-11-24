from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method

# from shlex import quote
# from kubernetes import client, config


class Solutions(BaseActor):
    def _filter_data(self, deployment):
        status = "Running"
        for status_obj in deployment["status"]["conditions"]:
            if status_obj["status"] == "False":
                status = "Error"
                break
        # TODO: Add vdc name
        filtered_deployment = {
            "Release": deployment["metadata"]["labels"]["app.kubernetes.io/instance"],
            "Version": deployment["metadata"]["labels"]["app.kubernetes.io/version"],
            "Creation Timestamp": deployment["metadata"]["creationTimestamp"],
            "Status": status,
            "Status Details": deployment["status"]["conditions"],
        }
        return filtered_deployment

    def _list_all_solutions(self) -> list:
        """List all deployments from kubectl and corresponding helm list info

        """
        all_deployments = []
        # for vdc in all_vdcs:
        # TODO loop over all vdc instances and get config path
        vdc_info = {}  # TODO to be removed
        vdc_info["kube_config_path"] = f"{j.core.dirs.HOMEDIR}/.kube/config"  # TODO to be removed
        config_path = vdc_info["kube_config_path"]
        k8s_client = j.sals.kubernetes.Manager(config_path=vdc_info["kube_config_path"])

        # Get all deployments
        kubectl_deployment_info = k8s_client.execute_native_cmd(
            cmd=f"kubectl --kubeconfig {config_path} get deployments -o json"
        )
        deployments = j.data.serializers.json.loads(kubectl_deployment_info)["items"]

        for deployment_info in deployments:
            deployment_info = self._filter_data(deployment_info)
            release_name = deployment_info["Release"]
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)

            deployment_info.update({"User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values)})
            all_deployments.append(deployment_info)

        return all_deployments

    def _list_solutions(self, solution_type: str = None) -> list:
        """
        List deployments for specific solution type selected from kubectl and corresponding helm list info

        """
        all_deployments = []
        # for vdc in all_vdcs:
        # TODO loop over all vdc instances and get config path
        vdc_info = {}  # TODO to be removed
        vdc_info["kube_config_path"] = f"{j.core.dirs.HOMEDIR}/.kube/config"  # TODO to be removed
        config_path = vdc_info["kube_config_path"]
        k8s_client = j.sals.kubernetes.Manager(config_path=vdc_info["kube_config_path"])
        # Get deployments for specific solution type in k8s cluster
        # returns a json string
        # TODO: validate empty result
        kubectl_deployment_info = k8s_client.execute_native_cmd(
            cmd=f'kubectl --kubeconfig {config_path} get deployments -o=jsonpath=\'{{range .items[?(@.metadata.labels.app\.kubernetes\.io/name=="{solution_type}")]}}{{@}}{{"\\n"}}{{end}}\''
        )
        # TODO Improve splitting
        deployments = kubectl_deployment_info.split("\n")[:-1]

        for deployment_json_str in deployments:
            deployment_info = j.data.serializers.json.loads(deployment_json_str)
            deployment_info = self._filter_data(deployment_info)
            release_name = deployment_info["Release"]
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)
            deployment_host = k8s_client.execute_native_cmd(
                cmd=f"kubectl --kubeconfig {config_path} get ingress -o=jsonpath='{{.items[?(@.metadata.labels.app\.kubernetes\.io/instance==\"{release_name}\")].spec.rules[0].host}}'"
            )
            deployment_info.update(
                {
                    "Domain": deployment_host,
                    "User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values),
                }
            )
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
