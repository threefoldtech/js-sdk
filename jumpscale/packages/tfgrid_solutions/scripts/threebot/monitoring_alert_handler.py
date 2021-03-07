from io import StringIO
import binascii
import requests
from jumpscale.loader import j
import os


def _encode_data(data):
    keys = [
        "tid",
        "tname",
        "timestamp",
        "level",
        "message",
        "explorer_url",
        "vdc_name",
        "app_name",
        "status",
        "category",
        "type",
        "count",
    ]
    b = StringIO()
    for key in keys:
        if key in data:
            b.write(key)
            b.write(str(data.get(key)))
    return b.getvalue().encode()


def send_alert(alert):
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
            "app_name": alert.app_name,
            "status": alert.status,
            "category": alert.category,
            "message": alert.message,
            "level": alert.level,
            "timestamp": alert.last_occurrence,
            "count": alert.count,
            "type": alert.type,
            "tname": os.environ.get("VDC_OWNER_TNAME"),
        }
        encoded_data = _encode_data(data)
        signature = j.core.identity.me.nacl.signing_key.sign(encoded_data).signature
        signature = binascii.hexlify(signature).decode()
        data["signature"] = signature
        try:
            requests.post(f"{MONITORING_SERVER_URL}/alert", json=data)
        except Exception as e:
            j.logger.error(f"Failed to send alert, URL:{MONITORING_SERVER_URL}/alert, exception: {str(e)}")
