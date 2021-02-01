from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import get_user_info


def _filter_data(deployment):
    status = "Running"
    conditions = deployment["status"].get("conditions", [])
    for status_obj in conditions:
        if status_obj["status"] == "False":
            status = "Error"
            break

    creation_time = j.data.time.get(deployment["metadata"]["creationTimestamp"]).timestamp
    # TODO: Add VDC name
    filtered_deployment = {
        "Release": deployment["metadata"]["labels"].get("app.kubernetes.io/instance"),
        "Version": deployment["metadata"]["labels"].get("app.kubernetes.io/version"),
        "creation": creation_time,
        "Status": status,
        "Status Details": conditions,
    }
    return filtered_deployment


def get_all_deployments() -> list:
    """List all deployments from kubectl and corresponding helm list info"""
    all_deployments = []
    username = j.data.serializers.json.loads(get_user_info()).get("username")
    vdc_names = [vdc.vdc_name for vdc in j.sals.vdc.list(username)]
    for vdc_name in vdc_names:
        config_path = j.sals.fs.expanduser("~/.kube/config")
        k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
        # Get all deployments
        kubectl_deployment_info = k8s_client.execute_native_cmd(cmd=f"kubectl get deployments -o json")
        deployments = j.data.serializers.json.loads(kubectl_deployment_info)["items"]

        kubectl_statefulset_info = k8s_client.execute_native_cmd(cmd=f"kubectl get statefulset -o json")
        kubectl_statefulset_info = j.data.serializers.json.loads(kubectl_statefulset_info)["items"]

        deployments.extend(kubectl_statefulset_info)
        deployment_names = []
        for deployment_info in deployments:
            if "app.kubernetes.io/name" not in deployment_info["metadata"]["labels"]:
                continue

            solution_type = deployment_info["metadata"]["labels"]["app.kubernetes.io/name"]
            deployment_info = _filter_data(deployment_info)
            release_name = deployment_info["Release"]
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)
            try:
                deployment_host = k8s_client.execute_native_cmd(
                    cmd=f"kubectl get ingress -l app.kubernetes.io/instance={release_name} -o=jsonpath='{{.items[0].spec.rules[0].host}}'"
                )
            except:
                pass

            deployment_info.update(
                {
                    "User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values),
                    "VDC Name": vdc_name,
                    "Domain": deployment_host,
                    "Chart": solution_type,
                }
            )
            all_deployments.append(deployment_info)
            deployment_names.append(release_name)

    return all_deployments


def get_deployments(solution_type: str = None, username: str = None) -> list:
    """
    List deployments for specific solution type selected from kubectl and corresponding helm list info

    """
    all_deployments = []
    username = username or j.data.serializers.json.loads(get_user_info()).get("username")
    vdc_names = [vdc.vdc_name for vdc in j.sals.vdc.list(username)]
    for vdc_name in vdc_names:
        config_path = j.sals.fs.expanduser("~/.kube/config")
        if not j.sals.fs.exists(config_path):
            continue
        k8s_client = j.sals.kubernetes.Manager(config_path=config_path)

        # get deployments
        kubectl_deployment_info = k8s_client.execute_native_cmd(
            cmd=f"kubectl get deployments -l app.kubernetes.io/name={solution_type} -o json"
        )
        kubectl_deployment_info = j.data.serializers.json.loads(kubectl_deployment_info)

        # get statefulsets if no result from deployments
        if not kubectl_deployment_info["items"]:
            kubectl_deployment_info = k8s_client.execute_native_cmd(
                cmd=f"kubectl get statefulset -l app.kubernetes.io/name={solution_type} -o json"
            )
            kubectl_deployment_info = j.data.serializers.json.loads(kubectl_deployment_info)

        deployments = kubectl_deployment_info["items"]
        releases = []
        for deployment_info in deployments:
            deployment_info = _filter_data(deployment_info)
            release_name = deployment_info["Release"]
            if release_name in releases:
                continue
            releases.append(release_name)
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)
            deployment_host = ""
            try:
                deployment_host = k8s_client.execute_native_cmd(
                    cmd=f"kubectl get ingress -l app.kubernetes.io/instance={release_name} -o=jsonpath='{{.items[0].spec.rules[0].host}}'"
                )
            except:
                pass

            deployment_info.update(
                {
                    "VDC Name": vdc_name,
                    "Domain": deployment_host,
                    "User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values),
                }
            )
            all_deployments.append(deployment_info)

    return all_deployments
