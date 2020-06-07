import binascii
from jumpscale.data.nacl import NACL, payload_build
from jumpscale.data.serializers import base64
from jumpscale.god import j


class Identity:
    def __init__(self):
        self.config_env = j.core.config.Environment()
        self._threebot_data = self.config_env.get_threebot_data()
        self._nacl = None
        self._tid = None

    def configure(self, name, email, path_to_words):
        j.config.configure_threebot(name, email, path_to_words)
        self._threebot_data = self.config_env.get_threebot_data()
        return self.tid

    @property
    def nacl(self):
        if not self._nacl:
            self.verify_configuration()
            priv_key = base64.decode(self._threebot_data["private_key"])
            self._nacl = NACL(private_key=priv_key)
        return self._nacl

    @property
    def tid(self):
        if not self._tid:
            self._tid = self._threebot_data.get("id") or self.register()
        return self._tid

    def verify_configuration(self):
        for key in ["private_key", "email", "name"]:
            if not self._threebot_data.get(key):
                raise j.exceptions.Value("Threebot not configured")

    def register(self, host=None):
        self.verify_configuration()
        explorer = j.clients.explorer.get_default()
        try:
            user = explorer.users.get(name=self._threebot_data["name"])
        except j.exceptions.NotFound:
            user = None

        if not user:
            if not host:
                try:
                    _, host = j.sals.nettools.get_default_ip_config()
                except Exception:
                    host = "localhost"

            user = explorer.users.new()
            user.name = self._threebot_data["name"]
            user.host = host
            user.email = self._threebot_data["email"]
            user.description = ""
            user.pubkey = self.nacl.get_verify_key_hex()
            try:
                tid = explorer.users.register(user)
            except Exception as e:
                msg = str(e)
                if msg.find("user with same name or email exists") != -1:
                    raise j.exceptions.Input("A user with same name or email exists om TFGrid phonebook.")
                raise e
            user = explorer.users.get(tid=tid)

        payload = payload_build(
            user.id, user.name, user.email, user.host, user.description, self.nacl.get_verify_key_hex()
        )
        _, signature = self.nacl.sign(payload)
        signature = binascii.hexlify(signature).decode()
        payload = binascii.hexlify(payload).decode()

        if not explorer.users.validate(user.id, payload, signature):
            raise j.exceptions.Input(
                "signature verification failed on TFGrid explorer, did you specify the right secret key?"
            )

        if self.nacl.get_verify_key_hex() != user.pubkey:
            raise j.exceptions.Input(
                "The verify key on your local system does not correspond with verify key on the TFGrid explorer"
            )

        # Add threebot id to config
        config = j.core.config.get_config()
        config["threebot"]["id"] = user.id
        j.core.config.update_config(config)

        return user.id


def get_identity():
    return Identity()


def export_module_as():
    return get_identity()
