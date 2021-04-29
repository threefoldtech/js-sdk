from functools import wraps
from json import JSONDecodeError
from urllib.parse import urlencode, quote, unquote

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


class StripPathMiddleware(object):
    """
    a middle ware for bottle apps to strip slashes
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, e, h):
        e["PATH_INFO"] = e["PATH_INFO"].rstrip("/")
        return self.app(e, h)


mainapp = Bottle()  # mount sub applications on this object
app = SessionMiddleware(mainapp, SESSION_OPTS)
app = StripPathMiddleware(app)
