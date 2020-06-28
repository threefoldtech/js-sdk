# i created new fake github account
# email: tft.testing.19@gmail.com.
# password: tft_password19
# username: tfttesting
# name: Codescalers Test
# organization: fakeForTest2

from jumpscale.god import j
from tests.base_tests import BaseTests


class GithubClientTest(BaseTests):
    def setUp(self):
        super().setUp()

        self.instance_name = j.data.random_names.random_name()

        self.username = "tfttesting"
        self.password = "tft_password19"
        self.email = "tft.testing.19@gmail.com"

        self.client = j.clients.github.get(self.instance_name)

        self.client.username = self.username
        self.client.password = self.password

    def test001_github_client_get_access(self):
        self.assertEqual(self.client.get_userdata()["emails"][0]["email"], self.email)

    def tearDown(self):
        j.clients.github.delete(self.instance_name)
