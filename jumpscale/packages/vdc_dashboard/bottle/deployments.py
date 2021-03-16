from beaker.middleware import SessionMiddleware
from bottle import Bottle, request, HTTPResponse, abort, redirect

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import (
    SESSION_OPTS,
    login_required,
    get_user_info,
    authenticated,
    package_authorized,
)
from jumpscale.packages.vdc_dashboard.bottle.models import UserEntry
from jumpscale.core.base import StoredFactory
from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.sals.vdc.size import VDC_SIZE
from jumpscale.sals.vdc.models import KubernetesRole

from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_all_deployments, get_deployments
import os
import math

app = Bottle()


def _get_vdc():
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc_full_name = list(j.sals.vdc.list_all())[0]
    vdc_instance = j.sals.vdc.get(vdc_full_name)
    return VDCFACTORY.find(vdc_name=vdc_instance.vdc_name, owner_tname=username, load_info=True)


def _get_addons(flavor, kubernetes_addons):
    """Get all the addons on the basic user plan
    Args:
        flavor(str): user flavor for the plan
        kubernetes_addons(list): all kubernetes nodes
    Returns:
        addons(list): list of addons used by the user over the basic chosen plan
    """
    plan = VDC_SIZE.VDC_FLAVORS.get(flavor)
    plan_nodes_count = plan.get("k8s").get("no_nodes")
    plan_nodes_size = plan.get("k8s").get("size")
    addons = list()
    for addon in kubernetes_addons:
        if addon.role != KubernetesRole.MASTER:
            if addon.size == plan_nodes_size:
                plan_nodes_count -= 1
                if plan_nodes_count < 0:
                    addons.append(addon)
            else:
                addons.append(addon)
    return addons


def _total_capacity(vdc):
    vdc.load_info()
    addons = _get_addons(vdc.flavor, vdc.kubernetes)
    plan = VDC_SIZE.VDC_FLAVORS.get(vdc.flavor)
    plan_nodes_count = plan.get("k8s").get("no_nodes")
    # total capacity = worker plan nodes + added nodes + master node
    return plan_nodes_count + len(addons) + 1


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
    if not wid:
        abort(400, "Error: Not all required params was passed.")
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc_full_name = list(j.sals.vdc.list_all())[0]
    vdc_instance = j.sals.vdc.get(vdc_full_name)
    vdc = VDCFACTORY.find(vdc_name=vdc_instance.vdc_name, owner_tname=username, load_info=True)
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    deployer = vdc.get_deployer()
    try:
        deployer.delete_k8s_node(wid)
    except j.exceptions.Input:
        abort(400, "Error: Failed to delete workload")
    return j.data.serializers.json.dumps({"result": True})


@app.route("/api/s3/expose")
@package_authorized("vdc_dashboard")
def expose_s3() -> str:
    vdc = _get_vdc()
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


@app.route("/api/threebot_vdc", method="GET")
@package_authorized("vdc_dashboard")
def threebot_vdc():
    vdc = _get_vdc()
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    vdc_dict = vdc.to_dict()
    vdc_dict["expiration_days"] = (vdc.expiration_date - j.data.time.now()).days
    vdc_dict["expiration_date"] = vdc.calculate_expiration_value(False)
    # Add wallet address
    wallet = vdc.prepaid_wallet
    balances = wallet.get_balance()
    balances_data = []
    for item in balances.balances:
        # Add only TFT balance
        if item.asset_code == "TFT":
            balances_data.append(
                {"balance": item.balance, "asset_code": item.asset_code, "asset_issuer": item.asset_issuer}
            )
    vdc_dict["total_capacity"] = _total_capacity(vdc)
    vdc_dict["wallet"] = {
        "address": wallet.address,
        "network": wallet.network.value,
        "secret": wallet.secret,
        "balances": balances_data,
    }
    vdc_dict["price"] = math.ceil(vdc.calculate_spec_price())

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict), status=200, headers={"Content-Type": "application/json"}
    )


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
    config_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{username.rstrip('.3bot')}/{vdc_name}.yaml"
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
    vdc = _get_vdc()
    if namespace == "default":
        k8s_client.delete_deployed_release(release=data["release"], vdc_instance=vdc, namespace=namespace)
    else:
        k8s_client.execute_native_cmd(f"kubectl delete ns {namespace}")
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
    vdc = _get_vdc()
    vdc_zdb_monitor = vdc.get_zdb_monitor()
    password = vdc_zdb_monitor.get_password()
    encryption_key = password[:32].encode().zfill(32).hex()
    ip_version = data.get("ip_version", 6)
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
            return HTTPResponse(
                status=400,
                message=f"unsupported ip version: {ip_version}",
                headers={"Content-Type": "application/json"},
            )
        data["groups"].append({"backends": [{"address": zdb_url, "namespace": zdb.namespace, "password": password}]})
    return j.data.serializers.json.dumps({"data": j.data.serializers.toml.dumps(data)})


@app.route("/api/zdb/secret", method="GET")
@authenticated
def get_zdb_secret():
    vdc = _get_vdc()
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
    cmds = [f"git checkout {branch}", "git pull"]
    for cmd in cmds:
        rc, out, err = j.sals.process.execute(cmd, cwd="/sandbox/code/github/threefoldtech/js-sdk")
        if rc:
            return HTTPResponse(
                j.data.serializers.json.dumps(
                    {"error": "failed to pull upstream", "stderr": err, "stdout": out, "code": rc, "cmd": cmd}
                ),
                status=500,
                headers={"Content-Type": "application/json"},
            )
    j.core.executors.run_tmux(
        "bash /sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/tfgrid_solutions/scripts/threebot/restart.sh 5",
        "restart",
    )
    return HTTPResponse(
        j.data.serializers.json.dumps({"success": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/check_update", method="GET")
@package_authorized("vdc_dashboard")
def check_update():
    try:
        response = j.tools.http.get("https://api.github.com/repos/threefoldtech/js-sdk/releases")
        json_response = j.data.serializers.json.loads(response.text)
        latest_remote_tag = json_response[0]["tag_name"]
    except Exception as e:
        raise j.exceptions.Runtime(f"Failed to fetch remote releases. {str(e)}")

    vdc_dashboard_path = j.packages.vdc_dashboard.__file__
    sdk_repo_path = j.tools.git.find_git_path(vdc_dashboard_path)
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


app = SessionMiddleware(app, SESSION_OPTS)
