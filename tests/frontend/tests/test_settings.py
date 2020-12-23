import pytest
from tests.frontend.pages.settings.settings import Settings
from tests.frontend.tests.base_tests import BaseTest
from jumpscale.loader import j


@pytest.mark.integration
class SettingsTests(BaseTest):
    def test01_add_admins(self):
        """Test case for adding an admin and deleting it.

        **Test Scenario**

        - Add an admin.
        - Check that the admin has been added in the admins.
        - Delete the admin.
        - Check that the admin has been deleted from the admins.
        """
        settings = Settings(self.driver)
        settings.load()

        self.info("Add an admin")
        admin = f"{self.random_name()}.3bot"
        settings.add_admin(admin)

        self.info("Check that the admin has been added in the admins")
        admins = settings.list("Admins")
        self.assertIn(admin, admins.keys())

        self.info("Delete the admin")
        settings.delete_admin(admin)

        self.info("Check that the admin has been deleted from the admins")
        admins = settings.list("Admins")
        self.assertNotIn(admin, admins.keys())

    def test02_add_identity(self):
        """Test case for adding an identity and deleting it.

        **Test Scenario**

        - Add an identity.
        - Check that the identity has been added in the identities.
        - Delete the identity.
        - Check that the identity has been deleted from the identities.
        """
        settings = Settings(self.driver)
        settings.load()

        self.info("Add an identity")
        name = self.random_name()
        settings.add_identities(name, self.tname, self.email, self.words)

        self.info("Check that the identity has been added in the identities")
        identities = settings.list("Identities")
        self.assertIn(name, identities.keys())

        self.info("Delete the identity")
        settings.delete_identity(name)

        self.info("Check that the identity has been deleted from the identities")
        identities = settings.list("Identities")
        self.assertNotIn(name, identities.keys())

    def test03_add_escalation_emails(self):
        """Test case for adding an email and deleting it.

        **Test Scenario**

        - Add an email.
        - Check that the email has been added in the escalation emails.
        - Delete the email.
        - Check that the email has been deleted from the escalation emails.
        """

        settings = Settings(self.driver)
        settings.load()

        self.info("Add an email")
        email = j.data.fake.email()
        settings.add_escalation_emails(email)

        self.info("Check that the email has been added in the escalation emails")
        emails = settings.list("Escalation Emails")
        self.assertIn(email, emails.keys())

        self.info("Delete the email")
        settings.delete_escalation_emails(email)

        self.info("Check that the email has been deleted from the escalation emails")
        emails = settings.list("Escalation Emails")
        self.assertNotIn(email, emails.keys())
