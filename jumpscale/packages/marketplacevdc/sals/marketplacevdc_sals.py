from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import get_user_info


def _filter_data(deployment):
    status = "Running"
    for status_obj in deployment["status"]["conditions"]:
        if status_obj["status"] == "False":
            status = "Error"
            break
    # TODO: Add vdc name
    filtered_deployment = {
        "Release": deployment["metadata"]["labels"]["app.kubernetes.io/instance"],
        "Version": deployment["metadata"]["labels"].get("app.kubernetes.io/version"),
        "Creation Timestamp": deployment["metadata"]["creationTimestamp"],
        "Status": status,
        "Status Details": deployment["status"]["conditions"],
    }
    return filtered_deployment


def get_all_deployments() -> list:
    """List all deployments from kubectl and corresponding helm list info

    """
    all_deployments = []
    username = j.data.serializers.json.loads(get_user_info()).get("username")
    vdc_names = [vdc.vdc_name for vdc in j.sals.vdc.list(username)]
    for vdc_name in vdc_names:
        config_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{username.rstrip('.3bot')}/{vdc_name}.yaml"

        k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
        # Get all deployments
        kubectl_deployment_info = k8s_client.execute_native_cmd(
            cmd=f"kubectl --kubeconfig {config_path} get deployments -o json"
        )
        deployments = j.data.serializers.json.loads(kubectl_deployment_info)["items"]

        for deployment_info in deployments:
            deployment_info = _filter_data(deployment_info)
            release_name = deployment_info["Release"]
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)

            deployment_info.update(
                {
                    "User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values),
                    "VDC Name": vdc_name,
                }
            )
            all_deployments.append(deployment_info)

    return all_deployments


def get_deployments(solution_type: str = None) -> list:
    """
    List deployments for specific solution type selected from kubectl and corresponding helm list info

    """
    all_deployments = []
    username = j.data.serializers.json.loads(get_user_info()).get("username")
    vdc_names = [vdc.vdc_name for vdc in j.sals.vdc.list(username)]
    for vdc_name in vdc_names:
        config_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{username.rstrip('.3bot')}/{vdc_name}.yaml"
        k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
        # TODO: validate empty result
        kubectl_deployment_info = k8s_client.execute_native_cmd(
            cmd=f'kubectl --kubeconfig {config_path} get deployments -o=jsonpath=\'{{range .items[?(@.metadata.labels.app\.kubernetes\.io/name=="{solution_type}")]}}{{@}}{{"\\n"}}{{end}}\''
        )
        # TODO Improve splitting
        deployments = kubectl_deployment_info.split("\n")[:-1]

        for deployment_json_str in deployments:
            deployment_info = j.data.serializers.json.loads(deployment_json_str)
            deployment_info = _filter_data(deployment_info)
            release_name = deployment_info["Release"]
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)
            deployment_host = k8s_client.execute_native_cmd(
                cmd=f"kubectl --kubeconfig {config_path} get ingress -o=jsonpath='{{.items[?(@.metadata.labels.app\.kubernetes\.io/instance==\"{release_name}\")].spec.rules[0].host}}'"
            )
            deployment_info.update(
                {
                    "VDC Name": vdc_name,
                    "Domain": deployment_host,
                    "User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values),
                }
            )
            all_deployments.append(deployment_info)

    return all_deployments
