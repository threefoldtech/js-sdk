from beaker.middleware import SessionMiddleware
from bottle import Bottle, request, HTTPResponse, abort

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

from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_all_deployments, get_deployments
import os

app = Bottle()


def _get_vdc():
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc_full_name = list(j.sals.vdc.list_all())[0]
    vdc_instance = j.sals.vdc.get(vdc_full_name)
    return VDCFACTORY.find(vdc_name=vdc_instance.vdc_name, owner_tname=username, load_info=True)


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


@app.route("/api/deployments/<solution_type>")
@package_authorized("vdc_dashboard")
def list_deployments(solution_type: str) -> str:
    deployments = {}
    if solution_type:
        deployments = get_deployments(solution_type=solution_type)

    return j.data.serializers.json.dumps({"data": deployments})


@app.route("/api/deployments")
@package_authorized("vdc_dashboard")
def list_all_deployments() -> str:
    deployments = []
    try:
        deployments = get_all_deployments()
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
    vdc_dict["expiration_days"] = vdc.calculate_funded_period(False)
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

    vdc_dict["wallet"] = {
        "address": wallet.address,
        "network": wallet.network.value,
        "secret": wallet.secret,
        "balances": balances_data,
    }

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
        namespace=data["solution_type"],
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
    if not vdc_name:
        abort(400, "Error: Not all required params was passed.")
    config_path = j.sals.fs.expanduser("~/.kube/config")
    k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
    vdc = _get_vdc()
    k8s_client.delete_deployed_release(release=data["release"], vdc=vdc)
    j.sals.marketplace.solutions.cancel_solution_by_uuid(data["solution_id"])
    return j.data.serializers.json.dumps({"result": True})


@app.route("/api/zstor/config", method="POST")
@authenticated
def get_zstor_config():
    vdc = _get_vdc()
    vdc_zdb_monitor = vdc.get_zdb_monitor()
    password = vdc_zdb_monitor.get_password()
    data = {
        "data_shards": 2,
        "parity_shards": 1,
        "redundant_groups": 0,
        "redundant_nodes": 0,
        "encryption": {"algorithm": "AES", "key": "",},
        "compression": {"algorithm": "snappy",},
        "groups": [],
    }
    for zdb in vdc.s3.zdbs:
        data["groups"].append(
            {
                "backends": [
                    {"address": f"[{zdb.ip_address}]:{zdb.port}", "namespace": zdb.namespace, "password": password},
                ],
            }
        )
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


app = SessionMiddleware(app, SESSION_OPTS)
