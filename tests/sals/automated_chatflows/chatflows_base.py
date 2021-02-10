import os
import string

from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.admin.bottle.models import UserEntry as AdminUserEntry
from jumpscale.packages.marketplace.bottle.models import UserEntry as MarkerplaceUserEntry
from tests.base_tests import BaseTests
from solutions_automation import deployer


class ChatflowsBase(BaseTests):
    @classmethod
    def setUpClass(cls):
        # Load the needed packages here if it's needed.
        # set TEST_CERT and OVER_PROVISIONING to True.
        cls.test_cert = j.core.config.get("TEST_CERT", False)
        # cls.over_provisioning = j.core.config.get("OVER_PROVISIONING", False)
        cls.sort_nodes_by_sru = j.core.config.get("SORT_NODES_BY_SRU", False)
        j.core.config.set("TEST_CERT", True)
        # j.core.config.set("OVER_PROVISIONING", True)
        j.core.config.set("SORT_NODES_BY_SRU", True)
        # Get environment variables to create identity.
        cls.tname = os.environ.get("TNAME")
        cls.email = os.environ.get("EMAIL")
        cls.words = os.environ.get("WORDS")
        cls.wallet_secret = os.environ.get("WALLET_SECRET")
        cls.explorer_url = "https://explorer.devnet.grid.tf/api/v1"
        if not all([cls.tname, cls.email, cls.words, cls.wallet_secret]):
            raise Exception(
                "Please add (TNAME, EMAIL, WORDS) of your 3bot identity and WALLET_SECRET as environment variables"
            )

        # Import the wallet to be used for payment.
        cls.get_wallet(name="demos_wallet", secret=cls.wallet_secret)

        # Check if there is identity registered to set it back after the tests are finished.
        cls.me = None
        if j.core.identity.list_all() and hasattr(j.core.identity, "me"):
            cls.me = j.core.identity.me

        # Configure test identity and start threebot server.
        cls.identity_name = j.data.random_names.random_name()
        identity = j.core.identity.new(
            cls.identity_name, tname=cls.tname, email=cls.email, words=cls.words, explorer_url=cls.explorer_url
        )
        identity.register()
        identity.set_default()

        cls.server = j.servers.threebot.get("default")
        cls.server.start()

        # Timeout for any exposed solution to be reachable.
        cls.timeout = 60

    @classmethod
    def tearDownClass(cls):
        # Return TEST_CERT, OVER_PROVISIONING values after the tests are finished.
        j.core.config.set("TEST_CERT", cls.test_cert)
        # j.core.config.set("OVER_PROVISIONING", cls.over_provisioning)

        # Stop threebot server and the testing identity.
        cls.server.stop()
        j.core.identity.delete(cls.identity_name)

        # Restore the user identity
        if cls.me:
            j.core.identity.set_default(cls.me.instance_name)

    @staticmethod
    def get_wallet(name, secret):
        wallet = j.clients.stellar.get(name)
        wallet.secret = secret
        wallet.network = "STD"
        wallet.save()
        return wallet

    @staticmethod
    def random_name():
        # Only lower case for subdomain.
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)

    @classmethod
    def accept_terms_conditions(cls, type_):
        if type_ == "marketplace":
            explorer_url = j.core.identity.me.explorer.url
            if "testnet" in explorer_url:
                explorer_name = "testnet"
            elif "devnet" in explorer_url:
                explorer_name = "devnet"
            elif "explorer.grid.tf" in explorer_url:
                explorer_name = "mainnet"
            cls.user_entry_name = f"{explorer_name}_{cls.tname.replace('.3bot', '')}"
            cls.user_factory = StoredFactory(MarkerplaceUserEntry)
        else:
            cls.user_entry_name = f"{cls.tname.replace('.3bot', '')}"
            cls.user_factory = StoredFactory(AdminUserEntry)
        admin_user_entry = cls.user_factory.get(cls.user_entry_name)
        admin_user_entry.has_agreed = True
        admin_user_entry.tname = cls.tname
        admin_user_entry.save()
