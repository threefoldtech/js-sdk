from nacl.encoding import Base64Encoder
from .auth import HTTPSignatureAuth
from jumpscale.loader import j


class AlreadyConvertedError(j.core.exceptions.Input):
    pass


class Conversion:
    def __init__(self, client):
        self._client = client
        self._session = client._session

    def initialize(self, identity=None):
        me = identity if identity else j.core.identity.me

        url = self._client.url + "/reservations/convert"

        secret = me.nacl.signing_key.encode(Base64Encoder)
        auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"])
        headers = {"threebot-id": str(me.tid)}

        resp = self._session.get(url, auth=auth, headers=headers)

        if resp.status_code == 204:
            raise AlreadyConvertedError(f"convertion for user {me.tid} has already been done")

        return resp.json()

    def finalize(self, workloads, identity=None):
        me = identity if identity else j.core.identity.me

        url = self._client.url + "/reservations/convert"

        secret = me.nacl.signing_key.encode(Base64Encoder)
        auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"])
        headers = {"threebot-id": str(me.tid)}

        for w in workloads:
            print(w["result"])

        resp = self._session.post(url, json=workloads, auth=auth, headers=headers)
        return resp.json()
