import os
import math
from uuid import uuid4

from bottle import HTTPResponse, abort, redirect, request
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j

from jumpscale.packages.auth.bottle.auth import (
    authenticated,
    get_user_info,
    login_required,
    package_authorized,
)
from jumpscale.packages.vdc_dashboard.bottle.models import APIKeyFactory, UserEntry
from jumpscale.packages.vdc_dashboard.bottle.vdc_helpers import (
    _list_alerts,
    get_vdc,
    get_expiration_data,
    check_plan_autoscalable,
    get_wallet_info,
)
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import (
    get_all_deployments,
    get_deployments,
)

from .root import app


def _get_zstor_config(ip_version=6):
    vdc = get_vdc(True)
    vdc_zdb_monitor = vdc.get_zdb_monitor()
    password = vdc_zdb_monitor.get_password()
    encryption_key = password[:32].encode().zfill(32).hex()
    data = {
        "data_shards": 2,
        "parity_shards": 1,
        "redundant_groups": 0,
        "redundant_nodes": 0,
        "encryption": {"algorithm": "AES", "key": encryption_key},
        "compression": {"algorithm": "snappy"},
        "meta": {
            "type": "etcd",
            "config": {
                "endpoints": ["http://127.0.0.1:2379", "http://127.0.0.1:22379", "http://127.0.0.1:32379"],
                "prefix": "someprefix",
            },
        },
        "groups": [],
    }
    if ip_version == 4:
        deployer = vdc.get_deployer()
        vdc.load_info(load_proxy=True)
        deployer.s3.expose_zdbs()

    for zdb in vdc.s3.zdbs:
        if ip_version == 6:
            zdb_url = f"[{zdb.ip_address}]:{zdb.port}"
        elif ip_version == 4:
            zdb_url = zdb.proxy_address
        else:
            return
        data["groups"].append({"backends": [{"address": zdb_url, "namespace": zdb.namespace, "password": password}]})
    return data


@app.route("/api/kube/get")
@package_authorized("vdc_dashboard")
def get_kubeconfig() -> str:
    file_path = j.sals.fs.expanduser("~/.kube/config")
    if not j.sals.fs.exists(file_path):
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})

    file_content = j.sals.fs.read_file(file_path)

    if not file_content:
        return HTTPResponse(status=400, message="Invalid file!", headers={"Content-Type": "application/json"})

    return j.data.serializers.json.dumps({"data": file_content})


@app.route("/api/kube/nodes/delete", method="POST")
@package_authorized("vdc_dashboard")
def delete_node():
    data = j.data.serializers.json.loads(request.body.read())
    wid = data.get("wid")
    pods_to_delete = data.get("pods_to_delete")
    if not wid:
        abort(400, "Error: Not all required params was passed.")
    vdc = get_vdc()
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    deployer = vdc.get_deployer()

    # Delete pods that can't be redeployed on other nodes due to resources limitations
    for pod_ns in pods_to_delete:
        deployer.vdc_k8s_manager.execute_native_cmd(f"kubectl delete ns {pod_ns}")
        j.logger.info(f"{pod_ns} deleted")

    # Delete the node
    try:
        j.logger.info(f"Deleting node with wid: {wid}")
        deployer.delete_k8s_node(wid, True)
    except Exception as e:
        j.logger.error(f"Error: Failed to delete workload due to the following {str(e)}")
        abort(500, "Error: Failed to delete workload")
    return j.data.serializers.json.dumps({"result": True})


@app.route("/api/kube/nodes/check_before_delete", method="POST")
@package_authorized("vdc_dashboard")
def check_before_delete_node():
    data = j.data.serializers.json.loads(request.body.read())
    wid = data.get("wid")
    if not wid:
        abort(400, "Error: Not all required params was passed.")
    vdc = get_vdc()
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    deployer = vdc.get_deployer()
    try:
        is_ready, pods_to_delete = deployer.kubernetes.check_drain_availability(wid)
    except Exception as e:
        j.logger.error(f"Error: Failed to check before delete workload due to the following {str(e)}")
        abort(500, "Error: Failed to check before delete workload")
    return j.data.serializers.json.dumps({"is_ready": is_ready, "pods_to_delete": pods_to_delete})


@app.route("/api/s3/zdbs/delete", method="POST")
@package_authorized("vdc_dashboard")
def delete_zdb():
    data = j.data.serializers.json.loads(request.body.read())
    wid = data.get("wid")
    if not wid:
        abort(400, "Error: Not all required params was passed.")
    vdc = get_vdc()
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    deployer = vdc.get_deployer()
    try:
        j.logger.info(f"Deleting zdb with wid: {wid}")
        deployer.delete_s3_zdb(wid)
    except Exception as e:
        j.logger.error(f"Error: Failed to delete workload due to the following {str(e)}")
        abort(500, "Error: Failed to delete workload")
    return j.data.serializers.json.dumps({"result": True})


@app.route("/api/s3/expose")
@package_authorized("vdc_dashboard")
def expose_s3() -> str:
    vdc = get_vdc()
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})

    vdc_deployer = vdc.get_deployer()
    s3_domain = vdc_deployer.expose_s3()
    if not s3_domain:
        return HTTPResponse(status=400, message="Failed to expose S3", headers={"Content-Type": "application/json"})
    return j.data.serializers.json.dumps({"data": s3_domain})


@app.route("/api/deployments/<solution_type>", method="GET")
@package_authorized("vdc_dashboard")
def list_deployments(solution_type: str) -> str:
    deployments = {}
    if solution_type:
        deployments = get_deployments(solution_type=solution_type)

    return j.data.serializers.json.dumps({"data": deployments})


@app.route("/api/deployments", method="POST")
@package_authorized("vdc_dashboard")
def list_all_deployments() -> str:
    deployments = []
    data = j.data.serializers.json.loads(request.body.read())
    solution_types = data.get("solution_types")
    try:
        deployments = get_all_deployments(solution_types)
    except Exception as e:
        j.logger.exception(message=str(e), exception=e)

    return j.data.serializers.json.dumps({"data": deployments})


@app.route("/api/alerts", method="GET")
@package_authorized("vdc_dashboard")
def list_alerts() -> str:
    alerts = _list_alerts()
    return HTTPResponse(j.data.serializers.json.dumps(alerts), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/admins/list", method="GET")
@package_authorized("vdc_dashboard")
def list_all_admins() -> str:
    threebot = j.servers.threebot.get("default")
    package = threebot.packages.get("vdc_dashboard")
    admins = list(set(package.admins))
    return j.data.serializers.json.dumps({"data": admins})


@app.route("/api/admins/add", method="POST")
@package_authorized("vdc_dashboard")
def add_admin() -> str:
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    threebot = j.servers.threebot.get("default")
    package = threebot.packages.get("vdc_dashboard")
    if not name:
        raise j.exceptions.Value(f"Admin name shouldn't be empty")
    if name in package.admins:
        raise j.exceptions.Value(f"Admin {name} already exists")
    package.admins.append(name)
    threebot.packages.save()


@app.route("/api/admins/remove", method="POST")
@package_authorized("vdc_dashboard")
def remove_admin() -> str:
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    threebot = j.servers.threebot.get("default")
    package = threebot.packages.get("vdc_dashboard")
    if not name:
        raise j.exceptions.Value(f"Admin name shouldn't be empty")
    if name not in package.admins:
        raise j.exceptions.Value(f"Admin {name} does not exist")
    if len(package.admins) == 1:
        raise j.exceptions.Value(f"VDC should have at least one admin")
    j.logger.info(f"Removing admin {name}")
    package.admins.remove(name)
    threebot.packages.save()


@app.route("/api/vdc/info", method="GET")
@package_authorized("vdc_dashboard")
def vdc_capacity():
    vdc = get_vdc()
    vdc_dict = vdc.to_dict()
    for node in vdc_dict["kubernetes"]:
        if node["role"] == "master":
            node["status"] = j.sals.nettools.tcp_connection_test(node["public_ip"], 6443, 10)
    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/vdc/expiration", method="GET")
@package_authorized("vdc_dashboard")
def vdc_expiration():
    data = get_expiration_data()
    return HTTPResponse(j.data.serializers.json.dumps(data), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/vdc/plan/price", method="GET")
@package_authorized("vdc_dashboard")
def vdc_expiration():
    vdc = get_vdc()
    data = {"price": math.ceil(vdc.calculate_spec_price())}
    return HTTPResponse(j.data.serializers.json.dumps(data), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/vdc/plan/autoscalable", method="GET")
@package_authorized("vdc_dashboard")
def vdc_plan():
    data = {"autoscalable": check_plan_autoscalable()}
    return HTTPResponse(j.data.serializers.json.dumps(data), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/vdc/wallet", method="GET")
@package_authorized("vdc_dashboard")
def vdc_wallet_info():
    data = get_wallet_info()
    return HTTPResponse(j.data.serializers.json.dumps(data), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/deployments/install", method="POST")
@login_required
def install_deployment():
    # DEBUGGING PURPOSES
    data = j.data.serializers.json.loads(request.body.read())
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc_name = data.get("vdc_name")
    if not vdc_name:
        abort(400, "Error: Not all required params was passed.")
    config_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{j.data.text.removesuffix(username, '.3bot')}/{vdc_name}.yaml"
    k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
    k8s_client.add_helm_repo(data["repo_name"], data["repo_url"])
    k8s_client.update_repos()
    k8s_client.install_chart(
        release=data["release"],
        chart_name=data["chart_name"],
        namespace=f'{data["solution_type"]}-{data["release"]}',
        extra_config=data["config"],
    )
    return j.data.serializers.json.dumps({"result": True})


@app.route("/api/deployments/cancel", method="POST")
@login_required
def cancel_deployment():
    data = j.data.serializers.json.loads(request.body.read())
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc_name = data.get("vdc_name")
    namespace = data.get("namespace", "default")
    if not vdc_name:
        abort(400, "Error: Not all required params was passed.")
    config_path = j.sals.fs.expanduser("~/.kube/config")
    k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
    vdc = get_vdc()
    if namespace == "default":
        k8s_client.delete_deployed_release(release=data["release"], vdc_instance=vdc, namespace=namespace)
    else:
        k8s_client.execute_native_cmd(f"kubectl delete ns {namespace}")
    j.logger.info(f"Cancelling deployment for {data['solution_id']}")
    j.sals.marketplace.solutions.cancel_solution_by_uuid(data["solution_id"])
    return j.data.serializers.json.dumps({"result": True})


@app.route("/api/zstor/config", method="POST")
@authenticated
def get_zstor_config():
    data = dict()
    try:
        data = j.data.serializers.json.loads(request.body.read())
    except Exception as e:
        j.logger.error(f"couldn't load body due to error: {str(e)}.")
    ip_version = data.get("ip_version", 6)
    zstor_config = _get_zstor_config(ip_version)
    if not zstor_config:
        return HTTPResponse(
            status=400, message=f"unsupported ip version: {ip_version}", headers={"Content-Type": "application/json"}
        )
    return j.data.serializers.json.dumps({"data": j.data.serializers.toml.dumps(zstor_config)})


@app.route("/api/zdb/secret", method="GET")
@authenticated
def get_zdb_secret():
    vdc = get_vdc()
    vdc_zdb_monitor = vdc.get_zdb_monitor()
    password = vdc_zdb_monitor.get_password()
    return j.data.serializers.json.dumps({"data": password})


@app.route("/api/allowed", method="GET")
@authenticated
def allowed():
    user_factory = StoredFactory(UserEntry)
    user_info = j.data.serializers.json.loads(get_user_info())
    tname = user_info["username"]
    explorer_url = j.core.identity.me.explorer.url
    instances = user_factory.list_all()
    for name in instances:
        user_entry = user_factory.get(name)
        if user_entry.tname == tname and user_entry.explorer_url == explorer_url and user_entry.has_agreed:
            return j.data.serializers.json.dumps({"allowed": True})
    return j.data.serializers.json.dumps({"allowed": False})


@app.route("/api/accept", method="GET")
@login_required
def accept():
    user_factory = StoredFactory(UserEntry)

    user_info = j.data.serializers.json.loads(get_user_info())
    tname = user_info["username"]
    explorer_url = j.core.identity.me.explorer.url

    if "testnet" in explorer_url:
        explorer_name = "testnet"
    elif "devnet" in explorer_url:
        explorer_name = "devnet"
    elif "explorer.grid.tf" in explorer_url:
        explorer_name = "mainnet"
    else:
        return HTTPResponse(
            j.data.serializers.json.dumps({"error": f"explorer {explorer_url} is not supported"}),
            status=500,
            headers={"Content-Type": "application/json"},
        )

    user_entry = user_factory.get(f"{explorer_name}_{tname.replace('.3bot', '')}")
    if user_entry.has_agreed:
        return HTTPResponse(
            j.data.serializers.json.dumps({"allowed": True}), status=200, headers={"Content-Type": "application/json"}
        )
    else:
        user_entry.has_agreed = True
        user_entry.explorer_url = explorer_url
        user_entry.tname = tname
        user_entry.save()
        return HTTPResponse(
            j.data.serializers.json.dumps({"allowed": True}), status=201, headers={"Content-Type": "application/json"}
        )


@app.route("/api/update", method="GET")
@package_authorized("vdc_dashboard")
def update():
    branch_param = request.params.get("branch")
    if branch_param:
        branch = branch_param
    else:
        branch = os.environ.get("SDK_VERSION", "development")
    sdk_path = "/sandbox/code/github/threefoldtech/js-sdk"
    cmd = f"bash jumpscale/packages/vdc_dashboard/scripts/update.sh {branch}"
    rc, out, err = j.sals.process.execute(cmd, cwd=sdk_path, showout=True, timeout=1200)
    if rc:
        return HTTPResponse(
            j.data.serializers.json.dumps(
                {"error": "failed to pull upstream", "stderr": err, "stdout": out, "code": rc, "cmd": cmd}
            ),
            status=500,
            headers={"Content-Type": "application/json"},
        )
    j.core.executors.run_tmux(
        f"bash {sdk_path}/jumpscale/packages/tfgrid_solutions/scripts/threebot/restart.sh 5", "restart"
    )
    return HTTPResponse(
        j.data.serializers.json.dumps({"success": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/check_update", method="GET")
@package_authorized("vdc_dashboard")
def check_update():
    vdc_dashboard_path = j.packages.vdc_dashboard.__file__
    sdk_repo_path = j.tools.git.find_git_path(vdc_dashboard_path)
    try:
        _, out, _ = j.sals.process.execute("git ls-remote --tag | tail -n 1", cwd=sdk_repo_path)
        latest_remote_tag = out.split("/tags/")[-1].rstrip("\n")
    except Exception as e:
        raise j.exceptions.Runtime(f"Failed to fetch remote releases. {str(e)}")

    _, latest_local_tag, _ = j.sals.process.execute("git describe --tags --abbrev=0", cwd=sdk_repo_path)
    if latest_remote_tag != latest_local_tag.rstrip("\n"):
        return HTTPResponse(
            j.data.serializers.json.dumps({"new_release": latest_remote_tag}),
            status=200,
            headers={"Content-Type": "application/json"},
        )

    return HTTPResponse(
        j.data.serializers.json.dumps({"new_release": ""}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/backup", method="GET")
@package_authorized("vdc_dashboard")
def backup() -> str:
    from jumpscale.packages.vdc_dashboard.services.etcd_backup import service

    service.job()

    return HTTPResponse(
        j.data.serializers.json.dumps({"success": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/wallet/qrcode/get", method="POST")
@login_required
def get_wallet_qrcode_image():
    request_data = j.data.serializers.json.loads(request.body.read())
    address = request_data.get("address")
    amount = request_data.get("amount")
    scale = request_data.get("scale", 5)
    if not all([address, amount, scale]):
        return HTTPResponse("Not all parameters satisfied", status=400, headers={"Content-Type": "application/json"})

    data = f"TFT:{address}?amount={amount}&message=topup&sender=me"
    qrcode_image = j.tools.qrcode.base64_get(data, scale=scale)
    return j.data.serializers.json.dumps({"data": qrcode_image})


@app.route("/api/refer/<solution>", method="GET")
@login_required
def redir(solution):
    return redirect(f"/vdc_dashboard/#{solution}")


@app.route("/api/vdc/status", method="GET")
@login_required
def is_running():
    return HTTPResponse(
        j.data.serializers.json.dumps({"running": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/quantumstorage/enable", method="GET")
@login_required
def enable_quantumstorage():
    vdc = get_vdc()
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})

    qs = vdc.get_quantumstorage_manager()
    try:
        file_content = qs.apply()
        return HTTPResponse(
            j.data.serializers.json.dumps({"data": file_content}),
            status=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        j.logger.error(f"Failed to enable quantum storage on your vdc due to {str(e)}")
        return HTTPResponse(
            "Failed to enable quantum storage on your vdc", status=500, headers={"Content-Type": "application/json"}
        )


@app.route("/api/get_sdk_version", method="GET")
@login_required
def get_sdk_version():
    import importlib_metadata as metadata

    packages = ["js-ng", "js-sdk"]
    data = {}
    for package in packages:
        data[package] = metadata.version(package)
    return HTTPResponse(
        j.data.serializers.json.dumps({"data": data}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/api_keys", method="GET")
@login_required
def get_api_keys():
    api_keys = []
    for name in APIKeyFactory.list_all():
        api_key = APIKeyFactory.find(name)
        api_key = api_key.to_dict()
        api_key.pop("key")
        api_keys.append(api_key)
    return j.data.serializers.json.dumps({"data": api_keys})


@app.route("/api/api_keys", method="POST")
@login_required
def generate_api_keys():
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    role = data.get("role")
    if not name:
        return HTTPResponse(f"Please specify a name", status=500, headers={"Content-Type": "application/json"})
    if not role:
        return HTTPResponse(f"Please specify a role", status=500, headers={"Content-Type": "application/json"})

    if APIKeyFactory.find(name):
        return HTTPResponse(
            f"API key with name '{name}' is already exist", status=500, headers={"Content-Type": "application/json"}
        )
    api_key = APIKeyFactory.new(name.lower(), role=role)
    api_key.save()
    return j.data.serializers.json.dumps({"data": api_key.to_dict()})


@app.route("/api/api_keys", method="PUT")
@login_required
def edit_api_keys():
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    role = data.get("role")
    regenerate = data.get("regenerate")
    if not name:
        return HTTPResponse(f"Please specify a name", status=500, headers={"Content-Type": "application/json"})

    if not any([role, regenerate]) or all([role, regenerate]):
        return HTTPResponse(
            f"Please specify a role or set 'regenerate' to true to regenerate the key",
            status=500,
            headers={"Content-Type": "application/json"},
        )

    api_key = APIKeyFactory.find(name.lower())
    if not api_key:
        return HTTPResponse(
            f"API key with name '{name}' does not exist", status=500, headers={"Content-Type": "application/json"}
        )
    if role:
        api_key.role = role
        api_key.save()
    if regenerate:
        api_key.key = uuid4().hex
        api_key.save()
        return j.data.serializers.json.dumps({"data": api_key.to_dict()})


@app.route("/api/api_keys", method="DELETE")
@login_required
def delete_api_keys():
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    delete_all = data.get("all")
    if not any([name, delete_all]):
        return HTTPResponse(
            f"Please specify a name or set 'all' to true to delete all keys",
            status=500,
            headers={"Content-Type": "application/json"},
        )
    if name:
        if not APIKeyFactory.find(name):
            return HTTPResponse(
                f"API key with name '{name}' does not exist", status=500, headers={"Content-Type": "application/json"}
            )
        APIKeyFactory.delete(name)
    else:
        for api_key in APIKeyFactory.list_all():
            APIKeyFactory.delete(api_key)


@app.route("/api/redeploy_master", method="POST")
@package_authorized("vdc_dashboard")
def redeploy_master():
    data = j.data.serializers.json.loads(request.body.read())
    wid = data.get("wid")
    vdc = get_vdc()
    if not wid:
        deployer = vdc.get_deployer()
        w = deployer.kubernetes._get_latest_master_workload()
    else:
        zos = j.sals.zos.get()
        w = zos.workloads.get(wid)
    network_farm = j.sals.marketplace.deployer.get_pool_farm_name(w.info.pool_id)
    deployer = vdc.get_deployer(network_farm=network_farm)
    try:
        deployer.kubernetes.redeploy_master(w)
    except Exception as e:
        j.logger.exception("Failed to redeploy master", exception=e)
        return HTTPResponse(f"Failed to redeploy master", status=500, headers={"Content-Type": "application/json"})
