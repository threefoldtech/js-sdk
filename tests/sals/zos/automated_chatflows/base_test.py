from jumpscale.core.base import Base
from jumpscale.loader import j

import string


def random_string():
    return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)


def info(msg):
    j.logger.info(msg)
