from functools import wraps
from json import JSONDecodeError
from urllib.parse import urlencode

import nacl
import requests
from beaker.middleware import SessionMiddleware
from bottle import Bottle, abort, redirect, request, response
from nacl.public import Box
from nacl.signing import VerifyKey

from jumpscale.loader import j

SESSION_OPTS = {"session.type": "file", "session.data_dir": f"{j.core.dirs.VARDIR}/data", "session.auto": True}
REDIRECT_URL = "https://login.threefold.me"
CALLBACK_URL = "/auth/3bot_callback"
LOGIN_URL = "/auth/login"

app = Bottle()


templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "templates")
env = j.tools.jinja2.get_env(templates_path)


@app.route("/login")
def login():
    """List available providers for login and redirect to the selected provider (3bot connect)

    Returns:
        Renders the template of login page
    """
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
            "scope": j.data.serializers.json.dumps({"user": True, "email": True}),
            "redirecturl": CALLBACK_URL,
            "publickey": j.core.identity.me.nacl.public_key.encode(encoder=nacl.encoding.Base64Encoder),
        }
        params = urlencode(params)
        return redirect(f"{REDIRECT_URL}?{params}", code=302)

    return env.get_template("login.html").render(providers=[], next_url=next_url)


@app.route("/3bot_callback")
def callback():
    """Takes the response from the provider and verify the identity of the logged in user

    Returns:
        Redirect to the wanted page after authentication
    """
    session = request.environ.get("beaker.session")
    data = request.query.get("signedAttempt")

    if not data:
        return abort(400, "signedAttempt parameter is missing")

    data = j.data.serializers.json.loads(data)

    if "signedAttempt" not in data:
        return abort(400, "signedAttempt value is missing")

    username = data["doubleName"]

    if not username:
        return abort(400, "DoubleName is missing")

    res = requests.get(f"https://login.threefold.me/api/users/{username}", {"Content-Type": "application/json"})
    if res.status_code != 200:
        return abort(400, "Error getting user pub key")
    pub_key = res.json()["publicKey"]

    user_pub_key = VerifyKey(j.data.serializers.base64.decode(pub_key))

    # verify data
    signedData = data["signedAttempt"]

    verifiedData = user_pub_key.verify(j.data.serializers.base64.decode(signedData)).decode()

    data = j.data.serializers.json.loads(verifiedData)

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

    nonce = j.data.serializers.base64.decode(data["data"]["nonce"])
    ciphertext = j.data.serializers.base64.decode(data["data"]["ciphertext"])

    try:
        priv = j.core.identity.me.nacl.private_key
        box = Box(priv, user_pub_key.to_curve25519_public_key())
        decrypted = box.decrypt(ciphertext, nonce)
    except nacl.exceptions.CryptoError:
        return abort(400, "Error decrypting data")

    try:
        result = j.data.serializers.json.loads(decrypted)
    except JSONDecodeError:
        return abort(400, "3Bot login returned faulty data")

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
    try:
        tid = j.sals.reservation_chatflow.reservation_chatflow.validate_user({"username": username, "email": email}).id
        session["tid"] = tid
        session["explorer"] = j.core.identity.me.explorer_url
    except Exception as e:
        j.logger.warning(
            f"Error in validating user: {username} with email: {email} in explorer: {j.core.identity.me.explorer_url}\n from {str(e)}"
        )

    return redirect(session.get("next_url", "/"))


@app.route("/logout")
def logout():
    """Invalidates the user session and redirect to login page

    Returns:
        Redirect to the login page
    """
    session = request.environ.get("beaker.session", {})
    try:
        session.invalidate()
    except AttributeError:
        pass

    next_url = request.query.get("next_url", "/")
    return redirect(f"{LOGIN_URL}?next_url={next_url}")


@app.route("/accessdenied")
def access_denied():
    """Displays the access denied page when the authenticated user is not authorized to view the page

    Returns:
        Renders access denied page
    """
    email = request.environ.get("beaker.session").get("email")
    next_url = request.query.get("next_url")
    return env.get_template("access_denied.html").render(email=email, next_url=next_url)


def get_user_info():
    """Parse user information from the session object

    Returns:
        [JSON string]: [user information session]
    """

    def _valid(tname, temail, explorer_url):
        if tname != j.core.identity.me.tname:
            return False
        if temail != j.core.identity.me.email:
            return False
        if explorer_url != j.core.identity.me.explorer_url:
            return False
        return True

    session = request.environ.get("beaker.session", {})
    tname = session.get("username", "")
    temail = session.get("email", "")
    tid = session.get("tid")
    explorer_url = session.get("explorer")
    # update tid in session when the identity changes
    if not _valid(tname, temail, explorer_url):
        session["tid"] = None
        session["explorer"] = j.core.identity.me.explorer_url
        try:
            session["tid"] = j.sals.reservation_chatflow.reservation_chatflow.validate_user(
                {"username": tname, "email": temail}
            ).id
        except Exception as e:
            j.logger.warning(
                f"Error in validating user: {tname} with email: {temail} in explorer: {j.core.identity.me.explorer_url}\n from {str(e)}"
            )
    session.get("signedAttempt", "")
    response.content_type = "application/json"
    return j.data.serializers.json.dumps(
        {
            "username": tname.lower(),
            "email": temail.lower(),
            "tid": tid,
            "devmode": not j.core.config.get_config().get("threebot_connect", True),
        }
    )


def is_admin(tname):
    """Checks if the user provided is considered an admin or not

    Args:
        tname (str): threebot name

    Returns:
        [Bool]: [True if the user is an admin]
    """
    threebot_me = j.core.identity.me
    return threebot_me.tname == tname or tname in threebot_me.admins


def authenticated(handler):
    """decorator for the methods to be for authenticated users only

    Args:
        handler (method)
    """

    def decorator(*args, **kwargs):
        session = request.environ.get("beaker.session")
        if j.core.config.get_config().get("threebot_connect", True):
            if not session.get("authorized", False):
                return abort(401)
        return handler(*args, **kwargs)

    return decorator


def admin_only(handler):
    """decorator for methods for admin access only

    Args:
        handler (method)
    """

    def decorator(*args, **kwargs):
        session = request.environ.get("beaker.session")
        if j.core.config.get_config().get("threebot_connect", True):
            username = session.get("username")
            if not is_admin(username):
                return abort(403)

        return handler(*args, **kwargs)

    return decorator


@app.route("/authenticated")
@authenticated
def is_authenticated():
    """get user information if it is authenticated

    Returns:
        [JSON string]: [user information session]
    """
    return get_user_info()


@app.route("/authorized")
@authenticated
@admin_only
def is_authorized():
    """get user information if it is authenticated and authorized as admin only

    Returns:
        [JSON string]: [user information session]
    """
    return get_user_info()


def login_required(func):
    """Decorator for the methods we want to secure

    Args:
        func (method)
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        session = request.environ.get("beaker.session")
        if j.core.config.get_config().get("threebot_connect", True):
            if not session.get("authorized", False):
                session["next_url"] = request.url
                return redirect(LOGIN_URL)
        return func(*args, **kwargs)

    return decorator


app = SessionMiddleware(app, SESSION_OPTS)
