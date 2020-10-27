import re

from jumpscale.loader import j


def is_message_matched(msg, pattern):
    if msg == pattern:
        return True
    else:
        try:
            return re.compile(pattern).match(msg)
        except Exception:
            return False


def read_file(filename):
    return j.sals.fs.read_file(j.sals.fs.expanduser(filename))


def write_file(filename, content):
    return j.sals.fs.write_file(j.sals.fs.expanduser(filename), content)
