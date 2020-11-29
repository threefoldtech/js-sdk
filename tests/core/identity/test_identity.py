from unittest import TestCase
from jumpscale.loader import j
import os


class TestIdentity(TestCase):
    def setUp(self):
        self.instance_name = j.data.random_names.random_name()
        self.me = None
        if j.core.identity.list_all() and hasattr(j.core.identity, "me"):
            self.me = j.core.identity.me

        self.tname = os.getenv("TNAME")
        self.email = os.getenv("EMAIL")
        self.words = os.getenv("WORDS")
        if not all([self.tname, self.email, self.words]):
            raise Exception("Please add (TNAME, EMAIL, WORDS) of your 3bot identity as environment variables")

    def _get_instance(self):
        return j.core.identity.new(
            self.instance_name,
            tname=self.tname,
            email=self.email,
            words=self.words,
            explorer_url="https://explorer.testnet.grid.tf/api/v1",
        )

    def test001_register(self):
        """Test case for register and check identity.

        **Test Scenario**

        - Get identity instance.
        - Register an instance.
        - Check about correct word and name.
        """
        identity = self._get_instance()
        id = identity.register()
        j.logger.info("Identity registered")

        self.assertTrue(id, j.core.identity.get(self.instance_name)._tid)

        self.assertTrue(self.tname, j.core.identity.find(self.instance_name).tname)

        self.assertTrue(self.email, j.core.identity.find(self.instance_name).email)
        self.assertTrue(self.words, j.core.identity.find(self.instance_name).words)

    def test002_set_default(self):
        """Test case for set my identity as default.

        **Test Scenario**

        - Get identity instance.
        - Register an instance.
        - Set my instance as default.
        - Check if identity.me it's same of my identity.
        """
        identity = self._get_instance()
        id = identity.register()
        j.core.identity.set_default(self.instance_name)
        j.logger.info("Identity registered")

        self.assertTrue(id, j.core.identity.me._tid)

        self.assertTrue(self.tname, j.core.identity.me.tname)

        self.assertTrue(self.email, j.core.identity.me.email)
        self.assertTrue(self.words, j.core.identity.me.words)

    def test003_delete(self):
        """Test case for delete my identity.

        **Test Scenario**

        - Get identity instance.
        - Register an instance.
        - Delete my identity.
        - Search if my identity exist or not.
        """
        identity = self._get_instance()
        identity.register()
        j.logger.info("Identity registered")

        self.assertTrue(self.tname, j.core.identity.find(self.instance_name).tname)

        j.core.identity.delete(self.instance_name)

        self.assertIsNone(j.core.identity.find(self.instance_name))

    def test004_register_fake_identity(self):
        """Test case for delete my identity.

        **Test Scenario**

        - Get identity instance.
        - Register an instance.
        - Delete my identity.
        - Search if my identity exist or not.
        """
        with self.assertRaises(j.core.exceptions.exceptions.Input):
            identity = j.core.identity.new(
                self.instance_name,
                tname=f"{self.instance_name}.3bot",
                email=self.email,
                words=self.words,
                explorer_url="https://explorer.testnet.grid.tf/api/v1",
            )

            identity.register()

    def tearDown(self):
        if self.me:
            self.me.set_default()
        j.core.identity.delete(self.instance_name)
