from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j


class SyncthingClient(Client):
    host = fields.String()
    port = fields.Integer()
    apikey = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__url = None
        self.__session = None
        self.__config = None

    @property
    def url(self):
        if not self.__url:
            self.__url = f"http://{self.host}:{self.port}/rest"
        return self.__url

    @property
    def config(self):
        if not self.__config:
            self.__config = self._call("system/config")
        return self.__config

    @property
    def session(self):
        if not self.__session:
            self.__session = j.tools.http.Session()
            self.__session.headers = {
                "Content-Type": "application/json",
                "User-Agent": "Syncthing Python client",
                "X-API-Key": self.apikey,
            }
        return self.__session

    def _call(self, endpoint, method="get", data=None, return_json=True):
        method_call = getattr(self.session, method)
        response = method_call(f"{self.url}/{endpoint}", json=data)
        response.raise_for_status()

        if return_json:
            return response.json()
        else:
            return response.content

    def restart(self):
        self._call("system/restart", "post")
        if not j.sals.nettools.wait_connection_test(self.host, self.port, timeout=3):
            j.exceptions.Timeout("Server didn't start in 3 seconds")

    def get_status(self):
        return self._call("system/status")

    def get_id(self):
        return self.get_status()["myID"]

    def reload_config(self):
        self.__config = None

    def set_config(self, config=None):
        self._call("system/config", "post", config or self.config, False)

    def get_folders(self):
        return self.config["folders"]

    def get_devices(self):
        return self.config["devices"]

    def _get_folder(self, name):
        for idx, folder in enumerate(self.get_folders()):
            if folder["id"] == name:
                return idx

    def _get_device(self, name):
        for idx, device in enumerate(self.get_devices()):
            if device["name"] == name:
                return idx

    def check_folder(self, name):
        return self._get_folder(name) is not None

    def check_device(self, name):
        return self._get_device(name) is not None

    def delete_folder(self, name):
        folders = self.get_folders()
        idx = self._get_folder(name)
        if idx:
            folders.pop(idx)
            return self.set_config(self.config)

    def delete_device(self, name):
        devices = self.get_devices()
        idx = self._get_device(name)
        if idx:
            devices.pop(idx)
            return self.set_config(self.config)

    def add_folder(
        self, name, path, ignore_perms=False, read_only=False, rescan_intervals=10, devices=None, overwrite=False,
    ):
        folders = self.get_folders()
        idx = self._get_folder(name)
        if idx:
            if overwrite:
                folders.pop(idx)
            else:
                raise j.exceptions.Input(f"Folder with name: {name} already exists")
        devices = devices or []
        my_id = self.get_id()
        if my_id not in devices:
            devices.append(my_id)
        devices = [{"deviceID": device} for device in devices]
        folder = {
            "autoNormalize": False,
            "copiers": 0,
            "devices": devices,
            "hashers": 0,
            "id": name,
            "ignoreDelete": False,
            "ignorePerms": ignore_perms,
            "invalid": "",
            "minDiskFreePct": 5,
            "order": "random",
            "path": path,
            "pullers": 0,
            "readOnly": read_only,
            "rescanIntervalS": rescan_intervals,
            "versioning": {"params": {}, "type": ""},
        }
        folders.append(folder)
        return self.set_config(self.config)

    def add_device(self, name, device_id, introducer=False, compression="always", overwrite=False):
        devices = self.get_devices()
        idx = self._get_device(name)
        if idx:
            if overwrite:
                devices.pop(idx)
            else:
                raise j.exceptions.Input(f"Device with name: {name} already exists")
        device = {
            "addresses": ["dynamic"],
            "certName": "",
            "compression": compression,
            "deviceID": device_id,
            "introducer": introducer,
            "name": name,
        }
        devices.append(device)
        return self.set_config(self.config)
