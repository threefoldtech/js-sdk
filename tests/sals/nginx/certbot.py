from jumpscale.sals.nginx.nginx import LetsencryptCertbot, ZerosslCertbot

from tests.base_tests import BaseTests


class CertbotTest(BaseTests):
    def test_create_zerossl_certbot(self):
        certbot = ZerosslCertbot(domain="example.com", email="name@example.com")
        cmd_list = certbot.run_cmd
        self.assertIn("--eab-kid", cmd_list)
        self.assertIn("--eab-hmac-key", cmd_list)
