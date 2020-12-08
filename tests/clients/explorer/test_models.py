from jumpscale.clients.explorer.models import DiskType, Container, Volume, ZdbNamespace, K8s


def test_container_ru():
    c = Container()
    tt = [
        {"cpu": 1, "memory": 2048, "type": DiskType.SSD, "size": 10240, "cru": 1, "mru": 2, "sru": 0, "hru": 0},
        {"cpu": 1, "memory": 2048, "type": DiskType.HDD, "size": 10240, "cru": 1, "mru": 2, "sru": 0, "hru": 0},
        {"cpu": 4, "memory": 4096, "type": DiskType.SSD, "size": 10240, "cru": 4, "mru": 4, "sru": 0, "hru": 0},
        {"cpu": 4, "memory": 4096, "type": DiskType.SSD, "size": 51200, "cru": 4, "mru": 4, "sru": 0, "hru": 0},
        {"cpu": 4, "memory": 4096, "type": DiskType.SSD, "size": 52224, "cru": 4, "mru": 4, "sru": 1, "hru": 0},
        {"cpu": 1, "memory": 1024, "type": DiskType.SSD, "size": 10000, "cru": 1, "mru": 1, "sru": 0, "hru": 0,},
    ]
    for tc in tt:
        c.capacity.cpu = tc["cpu"]
        c.capacity.memory = tc["memory"]
        c.capacity.disk_type = tc["type"]
        c.capacity.disk_size = tc["size"]

        ru = c.resource_units()
        assert ru.cru == tc["cru"]
        assert ru.mru == tc["mru"]
        assert ru.sru == tc["sru"]
        assert ru.hru == tc["hru"]


def test_volume_ru():
    v = Volume()
    tt = [
        {"size": 1, "type": DiskType.SSD, "cru": 0, "mru": 0, "sru": 1, "hru": 0},
        {"size": 1, "type": DiskType.HDD, "cru": 0, "mru": 0, "sru": 0, "hru": 1},
        {"size": 12, "type": DiskType.SSD, "cru": 0, "mru": 0, "sru": 12, "hru": 0},
    ]
    for tc in tt:
        v.size = tc["size"]
        v.type = tc["type"]

        ru = v.resource_units()
        assert ru.cru == tc["cru"]
        assert ru.mru == tc["mru"]
        assert ru.sru == tc["sru"]
        assert ru.hru == tc["hru"]


def test_zdb_ru():
    z = ZdbNamespace()
    tt = [
        {"size": 1, "type": DiskType.SSD, "cru": 0, "mru": 0, "sru": 1, "hru": 0},
        {"size": 1, "type": DiskType.HDD, "cru": 0, "mru": 0, "sru": 0, "hru": 1},
        {"size": 12, "type": DiskType.SSD, "cru": 0, "mru": 0, "sru": 12, "hru": 0},
    ]
    for tc in tt:
        z.size = tc["size"]
        z.disk_type = tc["type"]

        ru = z.resource_units()
        assert ru.cru == tc["cru"]
        assert ru.mru == tc["mru"]
        assert ru.sru == tc["sru"]
        assert ru.hru == tc["hru"]


def test_k8s_ru():
    z = K8s()
    tt = [{"size": 1, "cru": 1, "mru": 2, "sru": 50, "hru": 0}, {"size": 2, "cru": 2, "mru": 4, "sru": 100, "hru": 0}]
    for tc in tt:
        z.size = tc["size"]

        ru = z.resource_units()
        assert ru.cru == tc["cru"]
        assert ru.mru == tc["mru"]
        assert ru.sru == tc["sru"]
        assert ru.hru == tc["hru"]
