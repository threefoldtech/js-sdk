from bottle import redirect, request, abort, Bottle, response
import nacl
import requests
import json
from beaker.middleware import SessionMiddleware
import uuid
from jumpscale.god import j
from urllib.parse import urlencode
import base64
import binascii
from nacl.signing import VerifyKey
from nacl.public import Box
from functools import wraps

_session_opts = {"session.type": "file", "session.data_dir": "./data", "session.auto": True}
redirect_url = "https://login.threefold.me"
callback_url = "/auth/3bot_callback"
login_url = "/auth/login"

app = Bottle()


@app.route("/login")
def login():
    state = j.data.idgenerator.chars(20)
    session = request.environ.get("beaker.session")
    session["state"] = state
    app_id = request.get_header("host")
    params = {
        "state": state,
        "appid": app_id,
        "scope": json.dumps({"user": True, "email": True}),
        "redirecturl": callback_url,
        "publickey": j.core.identity.me.nacl.public_key.encode(encoder=nacl.encoding.Base64Encoder),
    }
    params = urlencode(params)
    return redirect(f"{redirect_url}?{params}", code=302)


@app.route("/3bot_callback")
def callback():
    session = request.environ.get("beaker.session")
    data = request.query.get("signedAttempt")

    if not data:
        return abort(400, "signedAttempt parameter is missing")

    data = json.loads(data)

    if "signedAttempt" not in data:
        return abort(400, "signedAttempt value is missing")

    username = data["doubleName"]

    if not username:
        return abort(400, "DoubleName is missing")

    res = requests.get(f"https://login.threefold.me/api/users/{username}", {"Content-Type": "application/json"})
    if res.status_code != 200:
        return abort(400, "Error getting user pub key")
    pub_key = res.json()["publicKey"]

    user_pub_key = VerifyKey(base64.b64decode(pub_key))

    # verify data
    signedData = data["signedAttempt"]

    verifiedData = user_pub_key.verify(base64.b64decode(signedData)).decode()

    data = json.loads(verifiedData)

    if "doubleName" not in data:
        return abort(400, "Decrypted data does not contain (doubleName)")

    if "signedState" not in data:
        return abort(400, "Decrypted data does not contain (state)")

    if data["doubleName"] != username:
        return abort(400, "username mismatch!")

    # verify state
    state = data["signedState"]
    if state != session["state"]:
        return abort(400, "Invalid state. not matching one in user session")

    nonce = base64.b64decode(data["data"]["nonce"])
    ciphertext = base64.b64decode(data["data"]["ciphertext"])

    try:
        priv = j.core.identity.me.nacl.private_key
        box = Box(priv, user_pub_key.to_curve25519_public_key())
        decrypted = box.decrypt(ciphertext, nonce)
    except nacl.exceptions.CryptoError:
        return abort(400, "Error decrypting data")

    try:
        result = json.loads(decrypted)
    except json.JSONDecodeError:
        return abort(400, "3bot login returned faulty data")

    if "email" not in result:
        return abort(400, "Email is not present in data")

    email = result["email"]["email"]

    sei = result["email"]["sei"]
    res = requests.post(
        "https://openkyc.live/verification/verify-sei",
        headers={"Content-Type": "application/json"},
        json={"signedEmailIdentifier": sei},
    )

    if res.status_code != 200:
        return abort(400, "Email is not verified")

    session["username"] = username
    session["email"] = email
    session["authorized"] = True
    session["signedAttempt"] = signedData
    return redirect(session.get("next_url", "/"))


@app.route("/logout")
def logout():
    session = request.environ.get("beaker.session", {})
    try:
        session.invalidate()
    except AttributeError:
        pass

    next_url = request.query.get("next_url", "/")
    return redirect(f"{login_url}?next_url={next_url}")


@app.route("/accessdenied")
def access_denied():
    email = request.environ.get("beaker.session").get("email")
    next_url = request.query.get("next_url")
    return {"error": "access denied."}


def get_user_info():
    session = request.environ.get("beaker.session", {})
    tname = session.get("username", "")
    temail = session.get("email", "")
    session.get("signedAttempt", "")
    response.content_type = "application/json"
    return j.data.serializers.json.dumps(
        {
            "username": tname.lower(),
            "email": temail.lower(),
            "devmode": not j.core.config.get("threebot").get(
                "THREEBOT_CONNECT", False
            ),  # TODO: fix after making threebot connect value
        }
    )


def is_admin(tname):
    threebot_me = j.core.identity.me
    return threebot_me.tname == tname or tname in threebot_me.admins


def authenticated(handler):
    def decorator(*args, **kwargs):
        session = request.environ.get("beaker.session")
        if j.core.config.get("threebot").get(
            "THREEBOT_CONNECT", False
        ):  # TODO: fix after making threebot connect value
            if not session.get("authorized", False):
                return abort(401)
        return handler(*args, **kwargs)

    return decorator


def admin_only(handler):
    def decorator(*args, **kwargs):
        session = request.environ.get("beaker.session")
        if j.core.config.get("threebot").get(
            "THREEBOT_CONNECT", False
        ):  # TODO: fix after making threebot connect value
            username = session.get("username")
            if not is_admin(username):
                return abort(403)

        return handler(*args, **kwargs)

    return decorator


@app.route("/auth/authenticated")
@authenticated
def is_authenticated():
    return get_user_info()


@app.route("/auth/authorized")
@authenticated
@admin_only
def is_authorized():
    return get_user_info()


def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        session = request.environ.get("beaker.session")
        # TODO: read threebot_connect from config and remove hardcoded True
        # if j.core.config.get_config().get("threebot", {}).get("threebot_connect"):
        if True:
            if not session.get("authorized", False):
                session["next_url"] = request.url
                return redirect(login_url)
        return func(*args, **kwargs)

    return decorator


app = SessionMiddleware(app, _session_opts)
