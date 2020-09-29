from unittest import TestCase
from jumpscale.loader import j
import os


class TestIdentity(TestCase):
    def setUp(self):
        self.instance_name = j.data.random_names.random_name()
        self.me = j.core.identity.me

    def _get_instance(self):
        if os.getenv("tname") and os.getenv("email") and os.getenv("words"):

            return j.core.identity.new(
                self.instance_name,
                tname=os.getenv("tname"),
                email=os.getenv("email"),
                words=os.getenv("words"),
                explorer_url="https://explorer.testnet.grid.tf/api/v1",
            )
        else:
            raise Exception("Please add (tname, email, words) of your 3bot identity as Env ")

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

        self.assertTrue(os.getenv("tname"), j.core.identity.find(self.instance_name).tname)

        self.assertTrue(os.getenv("email"), j.core.identity.find(self.instance_name).email)
        self.assertTrue(os.getenv("words"), j.core.identity.find(self.instance_name).words)

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

        self.assertTrue(os.getenv("tname"), j.core.identity.me.tname)

        self.assertTrue(os.getenv("email"), j.core.identity.me.email)
        self.assertTrue(os.getenv("words"), j.core.identity.me.words)

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

        self.assertTrue(os.getenv("tname"), j.core.identity.find(self.instance_name).tname)

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
                email=os.getenv("email"),
                words=os.getenv("words"),
                explorer_url="https://explorer.testnet.grid.tf/api/v1",
            )

            identity.register()

    def tearDown(self):
        if self.me:
            j.core.identity.set_default(self.me.instance_name)
        j.core.identity.delete(self.instance_name)
