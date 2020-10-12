import string
from unittest import TestCase

from jumpscale.loader import j


class BaseTests(TestCase):
    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    @staticmethod
    def random_string():
        return j.data.idgenerator.chars(10)

    @staticmethod
    def random_name():
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    @staticmethod
    def info(message):
        j.logger.info(message)
