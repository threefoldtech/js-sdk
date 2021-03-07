from urllib.parse import urlparse

import requests

from jumpscale.clients.explorer.models import User
from jumpscale.core import config as js_config
from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.core.config import get_config, update_config
from jumpscale.core.exceptions import Input, NotFound, Value
from jumpscale.data.encryption import mnemonic, generate_mnemonic
from jumpscale.data.nacl import NACL
from jumpscale.sals.nettools import get_default_ip_config

DEFAULT_EXPLORER_URLS = {
    "mainnet": "https://explorer.grid.tf/api/v1",
    "testnet": "https://explorer.testnet.grid.tf/api/v1",
    "devnet": "https://explorer.devnet.grid.tf/api/v1",
}

EXPLORER_URLS = js_config.set_default("explorer_api_urls", DEFAULT_EXPLORER_URLS)


class Identity(Base):
    def _explorer_url_update(self, value):
        if hasattr(self, "_explorer"):
            if self._explorer and self._explorer.url != value:
                self._explorer = None
        else:
            self._explorer = None

    _tid = fields.Integer(default=-1)
    words = fields.Secret()
    email = fields.String()
    tname = fields.String()
    explorer_url = fields.String(on_update=_explorer_url_update)
    admins = fields.List(fields.String())

    def __init__(
        self,
        tname=None,
        email=None,
        words=None,
        explorer_url=None,
        _tid=-1,
        admins=None,
        network=None,
        *args,
        **kwargs,
    ):
        """
        Get Identity

        Requires: tname, email and words or tid and words

        Arguments:
            tname (str, optional): Name eg. example.3bot
            email (str, optional): Email of identity
            words (str): Words used to secure identity
            explorer_url (str, optional): Url for the explorer to
            network (str, optional): network name (mainnet, testnet, devnet)
            tid (int, optional): When tid is passed tname, email will be verified against it

        Raises: NotFound incase tid is passed but does not exists on the explorer
        Raises: Input: when params are missing
        """
        self._explorer = None
        if not words:
            words = generate_mnemonic()
        if network is None and explorer_url is None:
            raise ValueError("network (mainnet, testnet, devnet) or explorer_url is required")

        if explorer_url is None:
            if network not in ["testnet", "mainnet", "devnet"]:
                raise ValueError("network should be one of (mainnet, testnet, devnet)")
            else:
                explorer_url = DEFAULT_EXPLORER_URLS[network]

        explorer_url = explorer_url.rstrip("/")
        super().__init__(
            tname=tname, email=email, words=words, explorer_url=explorer_url, _tid=_tid, admins=admins, *args, **kwargs,
        )
        self._nacl = None
        self.verify_configuration()

    @property
    def nacl(self):
        if not self._nacl:
            seed = mnemonic.mnemonic_to_key(self.words.strip())
            self._nacl = NACL(private_key=seed)
        return self._nacl

    def verify_configuration(self):
        """
        Verifies passed arguments to constructor

        Raises: NotFound incase tid is passed but does not exists on the explorer
        Raises: Input: when params are missing
        """
        if not self.words:
            raise Input("Words are mandotory for an indentity")
        if self._tid != -1:
            resp = requests.get(f"{self.explorer_url}/users/{self._tid}")
            resp.raise_for_status()
            user = User.from_dict(resp.json())
            if self.tname and self.tname != user.name:
                raise Input("Name of user does not match name in explorer")
            self.tname = user.name
            if self.nacl.get_verify_key_hex() != user.pubkey:
                raise Input(
                    "The verify key on your local system does not correspond with verify key on the TFGrid explorer"
                )
        else:
            for key in ["email", "tname"]:
                if not getattr(self, key):
                    raise Value(f"Threebot {key} not configured")

    @property
    def explorer(self):
        if self._explorer is None:
            from jumpscale.clients.explorer import export_module_as  # Import here to avoid circular imports

            ex_factory = export_module_as()

            # Backward compitablity (Update mainnet url)
            # Create new config has_migrated = True after mainnet update
            if not js_config.get("has_migrated_explorer_url", False):
                if urlparse(self.explorer_url).hostname == urlparse(EXPLORER_URLS["mainnet"]).hostname:
                    self.explorer_url = EXPLORER_URLS["mainnet"]
                    self.save()
                    js_config.set("has_migrated_explorer_url", True)

            if self.explorer_url:
                self.explorer_url = self.explorer_url.rstrip("/")
                self._explorer = ex_factory.get_by_url_and_identity(self.explorer_url, identity_name=self.instance_name)
            else:
                self._explorer = ex_factory.get_default()
                self.explorer_url = self._explorer.url
        return self._explorer

    @property
    def tid(self):
        if self._tid == -1:
            self.register()
        return self._tid

    def register(self, host=None):
        self.verify_configuration()

        # check if we are not already registered with the configured identity
        resp = requests.get(f"{self.explorer_url}/users?name={self.tname}")
        if resp.status_code == 404:
            user = None
        elif resp.status_code != 200:
            resp.raise_for_status()

        users = resp.json()
        if not users:
            user = None
        else:
            user = User.from_dict(users[0])

        tid = None
        if not user:
            if not host:
                try:
                    _, host = get_default_ip_config()
                except Exception:
                    host = "localhost"
            user = User()
            user.name = self.tname
            user.host = host
            user.email = self.email
            user.description = ""
            user.pubkey = self.nacl.get_verify_key_hex()

            resp = requests.post(f"{self.explorer_url}/users", json=user.to_dict())
            if resp.status_code == 409:  # conflict
                raise Input("A user with same name or email exists on TFGrid phonebook.")
            if resp.status_code != 201:
                resp.raise_for_status()

            tid = resp.json()["id"]
        else:
            if self.nacl.get_verify_key_hex() != user.pubkey:
                raise Input(
                    "The verify key on your local system does not correspond with verify key on the TFGrid explorer"
                )
            tid = user.id
        self._tid = tid
        if self.tname not in self.admins:
            self.admins.append(self.tname)
        self.save()
        return tid

    def set_default(self):
        from jumpscale.loader import j

        return j.core.identity.set_default(self.instance_name)


def get_identity():
    return IdentityFactory(Identity).me


class IdentityFactory(StoredFactory):
    _me = None

    def new(
        self, name, tname=None, email=None, words=None, explorer_url=None, tid=-1, admins=None, network=None,
    ):
        instance = super().new(
            name,
            tname=tname,
            email=email,
            words=words,
            explorer_url=explorer_url,
            _tid=tid,
            admins=admins,
            network=network,
        )
        instance.save()
        return instance

    @property
    def is_configured(self):
        return self._me is not None

    @property
    def me(self):
        if not self._me:
            config = get_config()
            default = config["threebot"]["default"]
            if default:
                self.__class__._me = self.get(name=default)
            else:
                for identity in self.list_all():
                    self.__class__._me = self.get(identity)
                    break
                else:
                    raise Value("No configured identity found")
        return self._me

    def set_default(self, name):
        config = get_config()
        config["threebot"]["default"] = name
        update_config(config)
        self.__class__._me = None


def export_module_as():
    return IdentityFactory(Identity)
