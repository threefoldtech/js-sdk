from unittest import TestCase
from jumpscale.loader import j
import os


class TestIdentity(TestCase):
    def setUp(self):
        self.instance_name = j.data.random_names.random_name()
        self.me = j.core.identity._me

    def _get_instance(self):
        if os.getenv("TNAME") and os.getenv("EMAIL") and os.getenv("WORDS"):

            return j.core.identity.new(
                self.instance_name,
                tname=os.getenv("TNAME"),
                email=os.getenv("EMAIL"),
                words=os.getenv("WORDS"),
                explorer_url="https://explorer.testnet.grid.tf/api/v1",
            )
        else:
            raise Exception("Please add (TNAME, EMAIL, WORDS) of your 3bot identity as environment variables ")

    def test001_register(self):
        """Test case for register and check identity.
        **Test scenario**
        #. Get identity instance.
        #. Register an instance.
        #. Check about correct word and name.
        """
        identity = self._get_instance()
        id = identity.register()
        j.logger.info("Identity registered")

        self.assertTrue(id, j.core.identity.get(self.instance_name)._tid)

        self.assertTrue(os.getenv("TNAME"), j.core.identity.find(self.instance_name).tname)

        self.assertTrue(os.getenv("EMAIL"), j.core.identity.find(self.instance_name).email)
        self.assertTrue(os.getenv("WORDS"), j.core.identity.find(self.instance_name).words)

    def test002_set_default(self):
        """Test case for set my identity as default.
        **Test scenario**
        #. Get identity instance.
        #. Register an instance.
        #. Set my instance as default.
        #. Check if identity.me it's same of my identity.
        """
        identity = self._get_instance()
        id = identity.register()
        j.core.identity.set_default(self.instance_name)
        j.logger.info("Identity registered")

        self.assertTrue(id, j.core.identity.me._tid)

        self.assertTrue(os.getenv("TNAME"), j.core.identity.me.tname)

        self.assertTrue(os.getenv("EMAIL"), j.core.identity.me.email)
        self.assertTrue(os.getenv("WORDS"), j.core.identity.me.words)

    def test003_delete(self):
        """Test case for delete my identity.
        **Test scenario**
        #. Get identity instance.
        #. Register an instance.
        #. Delete my identity.
        #. Search if my identity exist or not.
        """
        identity = self._get_instance()
        identity.register()
        j.logger.info("Identity registered")

        self.assertTrue(os.getenv("TNAME"), j.core.identity.find(self.instance_name).tname)

        j.core.identity.delete(self.instance_name)

        self.assertIsNone(j.core.identity.find(self.instance_name))

    def test004_register_fake_identity(self):
        """Test case for delete my identity.
        **Test scenario**
        #. Get identity instance.
        #. Register an instance.
        #. Delete my identity.
        #. Search if my identity exist or not.
        """
        with self.assertRaises(j.core.exceptions.exceptions.Input):
            identity = j.core.identity.new(
                self.instance_name,
                tname=f"{self.instance_name}.3bot",
                email=os.getenv("EMAIL"),
                words=os.getenv("WORDS"),
                explorer_url="https://explorer.testnet.grid.tf/api/v1",
            )

            identity.register()

    def tearDown(self):
        if self.me:
            j.core.identity.set_default(self.me.instance_name)
        j.core.identity.delete(self.instance_name)
