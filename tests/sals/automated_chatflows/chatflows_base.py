import os

from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.admin.bottle.models import UserEntry
from tests.base_tests import BaseTests


class ChatflowsBase(BaseTests):
    @classmethod
    def setUpClass(cls):
        # Load the needed packages here if it's needed.
        # set TEST_CERT and OVER_PROVISIONING to True.
        cls.test_cert = j.core.config.get("TEST_CERT", False)
        cls.over_provisioning = j.core.config.get("OVER_PROVISIONING", False)
        j.core.config.set("TEST_CERT", True)
        j.core.config.set("OVER_PROVISIONING", True)

        # Get environment variables to create identity.
        cls.tname = os.environ.get("TNAME")
        cls.email = os.environ.get("EMAIL")
        cls.words = os.environ.get("WORDS")
        cls.wallet_secret = os.environ.get("WALLET_SECRET")
        cls.explorer_url = "https://explorer.testnet.grid.tf/api/v1"
        if not all([cls.tname, cls.email, cls.words, cls.wallet_secret]):
            raise Exception(
                "Please add (TNAME, EMAIL, WORDS) of your 3bot identity and WALLET_SECRET as environment variables"
            )

        # Import the wallet to be used for payment.
        j.clients.stellar.get("demos_wallet", network="TEST", secret=cls.wallet_secret)

        # Check if there is identity registered to set it back after the tests are finished.
        cls.me = None
        if j.core.identity.list_all() and hasattr(j.core.identity, "me"):
            cls.me = j.core.identity.me

        # Accept T&C for testing identity.
        user_factory = StoredFactory(UserEntry)
        user_entry = user_factory.get(f"{cls.tname.replace('.3bot', '')}")
        user_entry.has_agreed = True
        user_entry.tname = cls.tname
        user_entry.save()

        # Configure test identity and start threebot server.
        cls.identity_name = j.data.random_names.random_name()
        identity = j.core.identity.new(
            cls.identity_name, tname=cls.tname, email=cls.email, words=cls.words, explorer_url=cls.explorer_url
        )
        identity.register()
        j.core.identity.set_default(cls.identity_name)
        cls.server = j.servers.threebot.get("default")
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        # Return TEST_CERT, OVER_PROVISIONING values after the tests are finished.
        j.core.config.set("TEST_CERT", cls.test_cert)
        j.core.config.set("OVER_PROVISIONING", cls.over_provisioning)

        # Stop threebot server and the testing identity.
        cls.server.stop()
        j.core.identity.delete(cls.identity_name)

        # Restore the user identity
        if cls.me:
            j.core.identity.set_default(cls.me.instance_name)

    @staticmethod
    def get_wallet(name, secret):
        return j.clients.stellar.get(name, network="TEST", secret=secret)
