from jumpscale.core import identity
from jumpscale.core.exceptions import NotFound

from .base import BaseResource
from .models import TfgridPhonebookUser1
from .pagination import get_all, get_page
from .auth import HTTPSignatureAuth
from nacl.encoding import Base64Encoder
from jumpscale.core import identity


class Users(BaseResource):
    _resource = "users"

    def _query(self, name=None, email=None):
        query = {}
        if name is not None:
            query["name"] = name
        if email is not None:
            query["email"] = email
        return query

    def iter(self, name=None, email=None):
        me = identity.get_identity()
        secret = me.nacl.signing_key.encode(Base64Encoder)

        auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"])
        headers = {"threebot-id": str(me.tid)}

        query = self._query(name=name,email=email)
        yield from get_all(self._session, TfgridPhonebookUser1, self._url, query, auth=auth, headers=headers)

    def list(self, name=None, email=None, page=None):
        query = self._query(name=name,email=email)
        if page:
            me = identity.get_identity()
            secret = me.nacl.signing_key.encode(Base64Encoder)

            auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"])
            headers = {"threebot-id": str(me.tid)}
            users, _ = get_page(self._session, page, TfgridPhonebookUser1, self._url, query, auth=auth, headers=headers)
        else:
            users = list(self.iter(name=name,email=email))
        return users

    def new(self):
        return TfgridPhonebookUser1()

    def register(self, user):
        resp = self._session.post(self._url, json=user.to_dict())
        return resp.json()["id"]

    def validate(self, tid, payload, signature):
        url = self._url + f"/users/{tid}/validate"
        data = {
            "payload": payload,
            "signature": signature,
        }

        resp = self._session.post(url, json=data)
        return resp.json()["is_valid"]

    def update(self, user, me=None):
        me = me or identity.get_identity()
        datatosign = ""
        datatosign += f"{user.id}{user.name}{user.email}"
        if user.host:
            datatosign += user.host
        datatosign += f"{user.description}{user.pubkey}"
        signature = me.nacl.sign_hex(datatosign.encode("utf8"))
        data = user.to_dict().copy()
        data["sender_signature_hex"] = signature.decode("utf8")
        self._session.put(f"{self._url}/{user.id}", json=data)

    def get(self, tid=None, name=None, email=None):
        if tid is not None:
            resp = self._session.get(f"{self._url}/{tid}")
            return TfgridPhonebookUser1.from_dict(resp.json())

        results = self.list(name=name, email=email)
        if results:
            return results[0]
        raise NotFound("user not found")
