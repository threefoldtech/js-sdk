from jumpscale.sals.vdc.models import VDCFACTORY
from beaker.middleware import SessionMiddleware
from bottle import Bottle, HTTPResponse
from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, login_required, get_user_info
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.core.base import StoredFactory

app = Bottle()


@app.route("/api/vdcs", method="GET")
@login_required
def list_vdcs():
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    result = []
    return HTTPResponse(
        j.data.serializers.json.dumps(
            [
                {
                    "vdc_name": "vdc02",
                    "owner_tname": username,
                    "solution_uuid": "9068617c9f0b46e893fd012425666585",
                    "identity_tid": 2914,
                    "flavor": "silver",
                    "created": 1606217515,
                    "updated": 1606217515,
                    "expiration": 1608809515,
                },
                {
                    "vdc_name": "vdc03",
                    "owner_tname": username,
                    "solution_uuid": "9068617c9f0b46e893fd012425666585",
                    "identity_tid": 2914,
                    "flavor": "silver",
                    "created": 1606217515,
                    "updated": 1606217515,
                    "expiration": 1608809515,
                },
            ]
        ),
        status=200,
        headers={"Content-Type": "application/json"},
    )
    for vdc in VDCFACTORY.list(username):
        vdc_dict = vdc.to_dict()
        vdc_dict.pop("s3")
        vdc_dict.pop("kubernetes")
        vdc_dict.pop("threebot")
        result.append(vdc_dict)
    return HTTPResponse(
        j.data.serializers.json.dumps(result), status=200, headers={"Content-Type": "application/json"},
    )


@app.route("/api/vdcs/<name>", method="GET")
@login_required
def get_vdc_info(name):
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    return HTTPResponse(
        j.data.serializers.json.dumps(
            {
                "vdc_name": name,
                "owner_tname": username,
                "solution_uuid": "9068617c9f0b46e893fd012425666585",
                "identity_tid": 2914,
                "flavor": "silver",
                "s3": {
                    "minio": {
                        "ip_address": "10.200.3.2",
                        "wid": 509541,
                        "node_id": "DyuhYMRR5c6PCPYTaFGpoN5iheo87ubKRvsLzinBzHHJ",
                        "pool_id": 5949,
                    },
                    "zdbs": [
                        {
                            "size": 10,
                            "wid": 509518,
                            "node_id": "8BFWcddW79cawvjnuUMw8M5s9FqS3pHhMHvzn3pgCUiB",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509519,
                            "node_id": "FDQJLM3NJCMzSdvb1qbigzotBg2WgSyLCJQFRAAyAP5e",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509520,
                            "node_id": "BDhpLyV28Y6Njy54WnB2Rkn6eHdEUbMu3GwTTs65rGAG",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509521,
                            "node_id": "DNav25NSCpx8NHwX11CUoUMsr2VW42sGoFCx6dtxyMV9",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509523,
                            "node_id": "2imakaznKfYx3vA4CDcTKxWbw9GcW3eXX8wQfr61X1Lz",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509524,
                            "node_id": "466X86s2ctLmL2Q6R7SrJ4VBMyt9h9zJDCSZhHUSQ9py",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509525,
                            "node_id": "2fi9ZZiBGW4G9pnrN656bMfW6x55RSoHDeMrd9pgSA8T",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509526,
                            "node_id": "A7FmQZ72h7FzjkJMGXmzLDFyfyxzitDZYuernGG97nv7",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509527,
                            "node_id": "72CP8QPhMSpF7MbSvNR1TYZFbTnbRiuyvq5xwcoRNAib",
                            "pool_id": 5949,
                        },
                        {
                            "size": 10,
                            "wid": 509528,
                            "node_id": "2m3nHPSAMyZFSeg5HPozic2NGBMtrXrBkhtNcVmd5Ss6",
                            "pool_id": 5949,
                        },
                    ],
                    "domain": None,
                },
                "kubernetes": [
                    {
                        "role": "master",
                        "size": 15,
                        "ip_address": "10.200.0.2",
                        "wid": 509522,
                        "node_id": "72CP8QPhMSpF7MbSvNR1TYZFbTnbRiuyvq5xwcoRNAib",
                        "pool_id": 5949,
                    },
                    {
                        "role": "worker",
                        "size": 15,
                        "ip_address": "10.200.2.2",
                        "wid": 509533,
                        "node_id": "3dAnxcykEDgKVQdTRKmktggL2MZbm3CPSdS9Tdoy4HAF",
                        "pool_id": 5949,
                    },
                ],
                "created": 1606217515,
                "updated": 1606217515,
                "expiration": 1608809515,
            }
        ),
        status=200,
        headers={"Content-Type": "application/json"},
    )
    vdc = VDCFACTORY.find(vdc_name=name, owner_tname=username, load_info=True)
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"},)
    vdc_dict = vdc.to_dict()
    vdc_dict.pop("threebot")
    return HTTPResponse(
        j.data.serializers.json.dumps(vdc.to_dict()), status=200, headers={"Content-Type": "application/json"},
    )


@app.route("/api/allowed", method="GET")
@login_required
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
