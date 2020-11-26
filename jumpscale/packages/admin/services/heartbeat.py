from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
import requests
import os
import binascii
from io import StringIO

VDC_NAME = os.environ.get("VDC_NAME", "")
EXPLORER_URL = os.environ.get("EXPLORER_URL", "")
MONITORING_SERVER_URL = os.environ.get("MONITORING_SERVER_URL")


class HeartBeatService(BackgroundService):
    # def __init__(self, name="heartbeat_service", interval=60 * 10, *args, **kwargs):
    def __init__(self, name="heartbeat_service", interval=10, *args, **kwargs):
        """
        Check disk space every 12 hours
        """
        super().__init__(name, interval, *args, **kwargs)

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
            data = {"tid": tid, "vdc_name": VDC_NAME, "explorer_url": EXPLORER_URL, "tname": j.core.identity.me.tid}
            encoded_data = self._encode_data(data)
            signature = j.core.identity.me.nacl.signing_key.sign(encoded_data).signature

            data["signature"] = binascii.hexlify(signature).decode()
            try:
                requests.post(
                    f"{MONITORING_SERVER_URL}/heartbeat", json=data, headers={"Content-type": "application/json"}
                )
            except Exception as e:
                j.logger.error(f"Failed to send alert, URL:{MONITORING_SERVER_URL}/heartbeat, exception: {str(e)}")


service = HeartBeatService()
