from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import get_user_info
import gevent


def _filter_data(deployment):
    status = "Running"
    conditions = deployment["status"].get("conditions", [])
    for status_obj in conditions:
        if status_obj["status"] == "False":
            status = "Error"
            break

    creation_time = j.data.time.get(deployment["metadata"]["creationTimestamp"]).format()
    # TODO: Add VDC name
    filtered_deployment = {
        "Release": deployment["metadata"]["labels"].get("app.kubernetes.io/instance"),
        "Version": deployment["metadata"]["labels"].get("app.kubernetes.io/version"),
        "Creation": creation_time,
        "Status": status,
        "Status Details": conditions,
    }
    return filtered_deployment


def _get_resource(k8s_client, resource_type, solution_type):
    resource = k8s_client.execute_native_cmd(
        cmd=f"kubectl get {resource_type} -A -l app.kubernetes.io/name={solution_type} -o json"
    )
    return j.data.serializers.json.loads(resource)["items"]


def _get_resource_key(k8s_client, resource_type, namespace, release_name, key):
    try:
        return k8s_client.execute_native_cmd(
            cmd=f"kubectl get {resource_type} -n {namespace} -l app.kubernetes.io/instance={release_name} -o=jsonpath='{{{key}}}'"
        )
    except:
        return None


def get_all_deployments(solution_types: list = None) -> list:
    """List all deployments from kubectl and corresponding helm list info"""
    if not solution_types:
        return []
    all_deployments = []
    username = j.data.serializers.json.loads(get_user_info()).get("username")

    def get_deployment(solution_type):
        solution_type_deployments = get_deployments(solution_type, username)
        all_deployments.extend(solution_type_deployments)

    threads = []
    for solution_type in solution_types:
        thread = gevent.spawn(get_deployment, solution_type)
        threads.append(thread)

    gevent.joinall(threads)

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
        resources = _get_resource(k8s_client, "deployments", solution_type)

        # get statefulsets if no result from deployments
        if not resources:
            resources = _get_resource(k8s_client, "statefulset", solution_type)

        releases = []
        for deployment_info in resources:
            namespace = deployment_info["metadata"].get("namespace", "default")
            deployment_info = _filter_data(deployment_info)
            release_name = deployment_info["Release"]
            if release_name in releases:
                continue
            releases.append(release_name)
            helm_chart_supplied_values = "{}"
            try:
                helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)
            except:
                pass
            domain = _get_resource_key(k8s_client, "ingress", namespace, release_name, ".items[0].spec.rules[0].host")

            if not domain:
                domain = _get_resource_key(
                    k8s_client, "ingressroutetcps", namespace, release_name, ".items[0].spec.tls.domains[0].main"
                )

            deployment_info.update(
                {
                    "VDC Name": vdc_name,
                    "Domain": domain,
                    "User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values),
                    "Chart": solution_type,
                    "Namespace": namespace,
                }
            )
            all_deployments.append(deployment_info)

    return all_deployments


def get_all_vdc_deployments(vdc_name):
    all_deployments = []
    config_path = j.sals.fs.expanduser("~/.kube/config")
    k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
    # Get all deployments
    kubectl_deployment_info = k8s_client.execute_native_cmd(cmd=f"kubectl get deployments -A -o json")
    deployments = j.data.serializers.json.loads(kubectl_deployment_info)["items"]

    kubectl_statefulset_info = k8s_client.execute_native_cmd(cmd=f"kubectl get statefulset -A -o json")
    kubectl_statefulset_info = j.data.serializers.json.loads(kubectl_statefulset_info)["items"]

    deployments.extend(kubectl_statefulset_info)
    deployment_names = []
    for deployment_info in deployments:
        if "app.kubernetes.io/name" not in deployment_info["metadata"]["labels"]:
            continue

        namespace = deployment_info["metadata"].get("namespace", "default")
        solution_type = deployment_info["metadata"]["labels"]["app.kubernetes.io/name"]
        deployment_info = _filter_data(deployment_info)
        release_name = deployment_info["Release"]
        helm_chart_supplied_values = "{}"
        try:
            helm_chart_supplied_values = k8s_client.get_helm_chart_user_values(release=release_name)
        except:
            pass
        deployment_host = ""
        try:
            deployment_host = k8s_client.execute_native_cmd(
                cmd=f"kubectl get ingress -n {namespace} -l app.kubernetes.io/instance={release_name} -o=jsonpath='{{.items[0].spec.rules[0].host}}'"
            )
        except:
            pass

        deployment_info.update(
            {
                "User Supplied Values": j.data.serializers.json.loads(helm_chart_supplied_values),
                "VDC Name": vdc_name,
                "Domain": deployment_host,
                "Chart": solution_type,
                "Namespace": namespace,
            }
        )
        all_deployments.append(deployment_info)
        deployment_names.append(release_name)
    return all_deployments
