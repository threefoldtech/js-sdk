import base64
import json
from functools import wraps
from urllib.parse import urlencode

import nacl
import requests
from beaker.middleware import SessionMiddleware
from bottle import Bottle, abort, redirect, request, response
from nacl.public import Box
from nacl.signing import VerifyKey

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jumpscale.god import j

SESSION_OPTS = {"session.type": "file", "session.data_dir": "./data", "session.auto": True}
REDIRECT_URL = "https://login.threefold.me"
CALLBACK_URL = "/auth/3bot_callback"
LOGIN_URL = "/auth/login"

app = Bottle()

templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(templates_path), autoescape=select_autoescape(["html", "xml"]))


@app.route("/login")
def login():
    session = request.environ.get("beaker.session")
    provider = request.query.get("provider")
    next_url = request.query.get("next_url", session.get("next_url"))

    if provider and provider == "3bot":
        state = j.data.idgenerator.chars(20)
        session["next_url"] = next_url
        session["state"] = state
        app_id = request.get_header("host")
        params = {
            "state": state,
            "appid": app_id,
            "scope": json.dumps({"user": True, "email": True}),
            "redirecturl": CALLBACK_URL,
            "publickey": j.core.identity.me.nacl.public_key.encode(encoder=nacl.encoding.Base64Encoder),
        }
        params = urlencode(params)
        return redirect(f"{REDIRECT_URL}?{params}", code=302)

    return env.get_template("login.html").render(providers=[], next_url=next_url)


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
    return redirect(f"{LOGIN_URL}?next_url={next_url}")


@app.route("/accessdenied")
def access_denied():
    email = request.environ.get("beaker.session").get("email")
    next_url = request.query.get("next_url")
    return env.get_template("access_denied.html").render(email=email, next_url=next_url)


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
                return redirect(LOGIN_URL)
        return func(*args, **kwargs)

    return decorator


app = SessionMiddleware(app, SESSION_OPTS)
