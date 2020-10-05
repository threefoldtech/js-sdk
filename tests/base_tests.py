from unittest import TestCase
from jumpscale.loader import j


class BaseTests(TestCase):
    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    def tearDown(self):
        pass

    @staticmethod
    def generate_random_text():
        return j.data.idgenerator.chars(10)

    def info(self, message):
        j.logger.info(message)
