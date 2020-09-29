import time
from unittest import TestCase
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver import ChromeOptions

from jumpscale.loader import j
from tests.frontend.pages.base import Base


class BaseTest(TestCase):
    @classmethod
    def setUpClass(cls):
        j.core.config.set("AUTO_LOGIN", True)
        cls.server = j.servers.threebot.get("default")
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        j.core.config.set("AUTO_LOGIN", False)
        cls.server.stop()

    def setUp(self):
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("ignore-certificate-errors")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        self.login_endpoint = "/auth/auto_login"
        self.driver.get(urljoin(Base.base_url, self.login_endpoint))

    def tearDown(self):
        if not self._outcome.success:
            self.driver.save_screenshot(f"{self._testMethodName}.png")
        self.driver.close()

    def info(self, msg):
        j.logger.info(msg)

    def random_str(self):
        return j.data.random_names.random_name()
