from jumpscale.core.exceptions import NotFound
from jumpscale.core import identity
from .models import TfgridPhonebookUser1
from .base import BaseResource


class Users(BaseResource):
    _resource = "users"

    def list(self, name=None, email=None):
        query = {}
        if name is not None:
            query["name"] = name
        if email is not None:
            query["email"] = email
        resp = self._session.get(self._url, params=query)
        users = []
        for user_data in resp.json():
            user = TfgridPhonebookUser1.from_dict(user_data)
            users.append(user)
        return users

    def new(self):
        return TfgridPhonebookUser1()

    def register(self, user):
        resp = self._session.post(self._url, json=user.to_dict())
        return resp.json()["id"]

    def validate(self, tid, payload, signature):
        url = self._base_url + f"/users/{tid}/validate"
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
