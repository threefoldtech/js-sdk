from jumpscale.loader import j
import os
from bottle import Bottle, request, template, redirect
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, login_required
import base64

app = Bottle()
templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "..", "frontend")


@app.route("/")
def index():
    session = request.environ.get("beaker.session", {})
    return template(f"{templates_path}/index.html", username=session.get("username", ""))


def create_or_update(collection, val, **tags):

    items = list(collection.find(**tags))
    if items:
        collection.update(items[0].id, val, tags)
    else:
        collection.set(val, tags)


@app.route("/upload", method="POST")
def do_upload():
    bcdb = j.clients.bcdb.get("default")
    collection = bcdb.collection("personal_docs")

    fname = request.forms.get("fname")
    lname = request.forms.get("lname")
    email = request.forms.get("email")
    id_card = request.files.get("id_card")
    passport = request.files.get("passport")

    create_or_update(collection, val=fname, **{"field_type": "fname"})
    create_or_update(collection, val=lname, **{"field_type": "lname"})
    create_or_update(collection, val=email, **{"field_type": "email"})
    create_or_update(collection, val=id_card.file.read(), **{"field_type": "ID_CARD"})
    create_or_update(collection, val=passport.file.read(), **{"field_type": "PASSPORT"})
    return redirect("/kyc/docs")


@app.route("/docs", method="GET")
def show_docs():
    bcdb = j.clients.bcdb.get("default")
    collection = bcdb.collection("personal_docs")
    items = list(collection.find(field_type="fname"))
    if items:
        fname = collection.get(items[0].id).data.decode()
    else:
        raise Exception("Can not find first name")

    items = list(collection.find(field_type="lname"))
    if items:
        lname = collection.get(items[0].id).data
    else:
        raise Exception("Can not find last name")

    items = list(collection.find(field_type="email"))
    if items:
        email = collection.get(items[0].id).data.decode()
    else:
        raise Exception("Can not find email")

    items = list(collection.find(field_type="ID_CARD"))
    if items:
        id_card = base64.b64encode(collection.get(items[0].id).data)
    else:
        raise Exception("Can not find ID card")
    items = list(collection.find(field_type="PASSPORT"))
    if items:
        passport = base64.b64encode(collection.get(items[0].id).data)
    else:
        raise Exception("Can not find passport")
    return template(
        f"{templates_path}/docs.html", fname=fname, lname=lname, email=email, id_card=id_card, passport=passport
    )
