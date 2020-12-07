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

app = Bottle()


@app.route("/api/deployments/<solution_type>")
@login_required
def list_deployments(solution_type: str) -> str:
    if solution_type:
        deployments = get_deployments(solution_type=solution_type)
    else:
        deployments = get_all_deployments()

    return j.data.serializers.json.dumps({"data": deployments})


@app.route("/api/threebot_vdc", method="GET")
@package_authorized("vdc_dashboard")
def threebot_vdc():
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc_full_name = list(j.sals.vdc.list_all())[0]
    vdc_instance = j.sals.vdc.get(vdc_full_name)
    vdc = VDCFACTORY.find(vdc_name=vdc_instance.vdc_name, owner_tname=username, load_info=True)
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    # Add wallet address
    vdc_dict = vdc.to_dict()
    vdc_dict.pop("threebot")
    wallet_address = j.clients.stellar.get(vdc_full_name).address
    vdc_dict["wallet_address"] = wallet_address
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
    config_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{username.rstrip('.3bot')}/{vdc_name}.yaml"
    k8s_client = j.sals.kubernetes.Manager(config_path=config_path)
    k8s_client.delete_deployed_release(data["release"])
    j.sals.marketplace.solutions.cancel_solution_by_uuid(data["solution_id"])
    return j.data.serializers.json.dumps({"result": True})


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


app = SessionMiddleware(app, SESSION_OPTS)
