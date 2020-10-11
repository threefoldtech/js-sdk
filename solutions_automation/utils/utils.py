import re
import os


def is_message_matched(msg, pattern):
    if msg == pattern:
        return True
    else:
        try:
            return re.compile(pattern).match(msg)
        except Exception:
            return False


def read_file(f):
    with open(os.path.expanduser(f), "r") as h:
        return h.read()


def write_file(filename, data):
    with open(os.path.expanduser(filename), "w") as f:
        return f.write(data)
