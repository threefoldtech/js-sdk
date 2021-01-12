import os

from jumpscale.loader import j
from jumpscale.packages import billing
from tests.base_tests import BaseTests


class VDCBase(BaseTests):
    @classmethod
    def setUpClass(cls):
        cls._get_env_vars()
        cls._import_wallet()
        cls._prepare_identity()
        cls._start_threebot_server()

    @classmethod
    def tearDownClass(cls):
        # Stop threebot server and the testing identity.
        cls.server.stop()
        j.core.identity.delete(cls.identity_name)

        # Restore the user identity
        if cls.me:
            j.core.identity.set_default(cls.me.instance_name)

    @classmethod
    def _get_env_vars(cls):
        needed_vars = ["TNAME", "EMAIL", "WORDS", "WALLET_SECRET", "VDC_NAME_USER", "VDC_NAME_TOKEN"]
        for var in needed_vars:
            value = os.environ.get(var)
            if not value:
                raise ValueError(f"Please add {var} as environment variables")
            setattr(cls, var.lower(), value)

    @classmethod
    def _import_wallet(cls):
        j.clients.stellar.get("test_wallet", network="STD", secret=cls.wallet_secret)

    @classmethod
    def _prepare_identity(cls):
        # Check if there is identity registered to set it back after the tests are finished.
        cls.me = None
        if j.core.identity.list_all() and hasattr(j.core.identity, "me"):
            cls.me = j.core.identity.me

        # Configure test identity and start threebot server.
        cls.explorer_url = "https://explorer.devnet.grid.tf/api/v1"
        cls.identity_name = j.data.random_names.random_name()
        identity = j.core.identity.new(
            cls.identity_name, tname=cls.tname, email=cls.email, words=cls.words, explorer_url=cls.explorer_url
        )
        identity.register()
        identity.set_default()

    @classmethod
    def _start_threebot_server(cls):
        cls.server = j.servers.threebot.get("default")
        path = j.sals.fs.dirname(billing.__file__)
        cls.server.packages.add(path)
        cls.server.start()

    @staticmethod
    def random_name():
        return j.data.random_names.random_name()
