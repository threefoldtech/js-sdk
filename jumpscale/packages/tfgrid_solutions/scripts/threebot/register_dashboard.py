from io import StringIO
import binascii
import requests
from jumpscale.loader import j
import os
import urllib.parse


def _encode_data(data):
    keys = [
        "tid",
        "tname",
        "explorer_url",
        "vdc_name",
    ]
    b = StringIO()
    for key in keys:
        if key in data:
            b.write(key)
            b.write(str(data.get(key)))
    return b.getvalue().encode()


def register_dashboard():
    VDC_NAME = os.environ.get("VDC_NAME", "")
    EXPLORER_URL = os.environ.get("EXPLORER_URL", "")
    MONITORING_SERVER_URL = os.environ.get("MONITORING_SERVER_URL")

    if MONITORING_SERVER_URL:
        identity_name = j.core.identity.me.instance_name
        tid = j.core.identity.get(identity_name).tid
        data = {
            "tid": tid,
            "explorer_url": EXPLORER_URL,
            "vdc_name": VDC_NAME,
            "tname": os.environ.get("VDC_OWNER_TNAME"),
        }
        encoded_data = _encode_data(data)
        signature = j.core.identity.me.nacl.signing_key.sign(encoded_data).signature
        signature = binascii.hexlify(signature).decode()
        data["signature"] = signature
        url = urllib.parse.urljoin(MONITORING_SERVER_URL, "register")
        try:
            req = requests.post(url, json=data)
            if req.status_code != 200:
                raise j.exceptions.Runtime(f"Failed to register dashboard with status code: {req.status_code}")
        except Exception as e:
            j.logger.error(f"Failed to register dashboard, URL:{url}, exception: {str(e)}")
