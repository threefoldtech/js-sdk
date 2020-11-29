from gevent import monkey

monkey.patch_all(subprocess=False)

from jumpscale.loader import j


def pytest_collection_modifyitems(items, config):
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker("unittests")
