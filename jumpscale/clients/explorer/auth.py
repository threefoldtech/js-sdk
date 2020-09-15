import base64
import time
from datetime import datetime
from email.utils import formatdate
from urllib.parse import urlparse

import requests.auth
from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey


class Signer:
    """
    Only supported signing algorithm is ed25519
    When using ed25519 algorithm, the secret is the base64-encoded private key
    """

    def __init__(self, secret):
        if isinstance(secret, str):
            secret = secret.encode()
        self._key = SigningKey(secret, encoder=Base64Encoder)

    @property
    def algorithm(self):
        return "ed25519"

    def sign(self, data):
        if isinstance(data, str):
            data = data.encode()
        signed = self._key.sign(data).signature
        return base64.b64encode(signed).decode()


class HeaderSigner(Signer):
    def __init__(self, key_id, secret, headers=None, sign_header="authorization"):
        super().__init__(secret=secret)
        self.headers = headers or ["date"]
        self.signature_template = build_signature_template(key_id, "ed25519", headers, sign_header)
        self.sign_header = sign_header

    def sign(self, headers, host=None, method=None, path=None):
        """
        Add Signature Authorization header to case-insensitive header dict.

        `headers` is a case-insensitive dict of mutable headers.
        `host` is a override for the 'host' header (defaults to value in
            headers).
        `method` is the HTTP method (required when using '(request-target)').
        `path` is the HTTP path (required when using '(request-target)').
        """
        headers = CaseInsensitiveDict(headers)
        required_headers = self.headers or ["date"]
        created = time.time()
        expires = created + 60
        dt = datetime.fromtimestamp(created)
        headers["date"] = formatdate(timeval=time.mktime(dt.timetuple()), localtime=False, usegmt=True)
        signable = generate_message(required_headers, headers, created, expires, host, method, path)
        signature = super().sign(signable)
        headers[self.sign_header] = self.signature_template % (signature, created, expires)
        return headers


class HTTPSignatureAuth(requests.auth.AuthBase):
    def __init__(self, key_id="", secret="", headers=None):
        headers = headers or []
        self.header_signer = HeaderSigner(key_id=key_id, secret=secret, headers=headers)
        self.uses_host = "host" in [h.lower() for h in headers]

    def __call__(self, r):
        headers = self.header_signer.sign(
            r.headers,
            # 'Host' header unavailable in request object at this point
            # if 'host' header is needed, extract it from the url
            host=urlparse(r.url).netloc if self.uses_host else None,
            method=r.method,
            path=r.path_url,
        )
        r.headers.update(headers)
        return r


# based on http://stackoverflow.com/a/2082169/151401
class CaseInsensitiveDict(dict):
    """ A case-insensitive dictionary for header storage.
        A limitation of this approach is the inability to store
        multiple instances of the same header. If that is changed
        then we suddenly care about the assembly rules in sec 2.3.
    """

    def __init__(self, d=None, **kwargs):
        super().__init__(**kwargs)
        if d:
            self.update((k.lower(), v) for k, v in d.items())

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())


def generate_message(required_headers, headers, created, expires, host=None, method=None, path=None):
    headers = CaseInsensitiveDict(headers)

    if not required_headers:
        required_headers = ["date"]

    signable_list = []
    for h in required_headers:
        h = h.lower()
        if h == "(request-target)":
            if not method or not path:
                raise Exception("method and path arguments required when " + 'using "(request-target)"')
            signable_list.append("%s: %s %s" % (h, method.lower(), path))

        elif h == "host":
            # 'host' special case due to requests lib restrictions
            # 'host' is not available when adding auth so must use a param
            # if no param used, defaults back to the 'host' header
            if not host:
                if "host" in headers:
                    host = headers[h]
                else:
                    raise Exception('missing required header "%s"' % h)
            signable_list.append("%s: %s" % (h, host))
        elif h == "(created)":
            signable_list.append("%s: %s" % (h, int(created)))
        elif h == "(expires)":
            signable_list.append("%s: %s" % (h, int(expires)))
        elif h == "date":
            if not headers.get(h):
                now = datetime.now()
                stamp = time.mktime(now.timetuple())
                date = formatdate(timeval=stamp, localtime=False, usegmt=True)
                headers[h] = date
            signable_list.append("%s: %s" % (h, headers[h]))
        else:
            if h not in headers:
                raise Exception('missing required header "%s"' % h)

            signable_list.append("%s: %s" % (h, headers[h]))

    signable = "\n".join(signable_list).encode("ascii")
    return signable


def build_signature_template(key_id, algorithm, headers, sign_header="authorization"):
    """
    Build the Signature template for use with the Authorization header.

    key_id is the mandatory label indicating to the server which secret to use
    algorithm is one of the six specified algorithms
    headers is a list of http headers to be included in the signing string.

    The signature must be interpolated into the template to get the final
    Authorization header value.
    """
    param_map = {"keyId": key_id, "algorithm": algorithm, "signature": "%s", "created": "%d", "expires": "%d"}
    if headers:
        headers = [h.lower() for h in headers]
        param_map["headers"] = " ".join(headers)
    kv = map('{0[0]}="{0[1]}"'.format, param_map.items())
    kv_string = ",".join(kv)
    if sign_header.lower() == "authorization":
        return "Signature {0}".format(kv_string)

    return kv_string
