from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
import requests
import os
import binascii
from io import StringIO
import urllib.parse

VDC_NAME = os.environ.get("VDC_NAME", "")
EXPLORER_URL = os.environ.get("EXPLORER_URL", "")
MONITORING_SERVER_URL = os.environ.get("MONITORING_SERVER_URL")


class HeartBeatService(BackgroundService):
    # def __init__(self, interval=60 * 10, *args, **kwargs):
    def __init__(self, interval=10, *args, **kwargs):
        """
        Check disk space every 10 seconds
        """
        super().__init__(interval, *args, **kwargs)

    def _encode_data(self, data):
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

    def job(self):
        if MONITORING_SERVER_URL:
            identity_name = j.core.identity.me.instance_name
            tid = j.core.identity.get(identity_name).tid
            data = {
                "tid": tid,
                "vdc_name": VDC_NAME,
                "explorer_url": EXPLORER_URL,
                "tname": os.environ.get("VDC_OWNER_TNAME"),
            }
            encoded_data = self._encode_data(data)
            signature = j.core.identity.me.nacl.signing_key.sign(encoded_data).signature

            data["signature"] = binascii.hexlify(signature).decode()
            url = urllib.parse.urljoin(MONITORING_SERVER_URL, "heartbeat")
            try:
                requests.post(url, json=data, headers={"Content-type": "application/json"})
            except Exception as e:
                j.logger.error(f"Failed to send heartbeat, URL:{url}, exception: {str(e)}")


service = HeartBeatService()
