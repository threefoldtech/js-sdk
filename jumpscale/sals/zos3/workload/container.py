from jumpscale.core.base import fields

from . import Data, DeviceType, Result


class Member(Data):
    SKIP_CHALLENGE = ["yggdrasil_ip"]

    network_id = fields.String()
    ips = fields.List(fields.IPAddress())
    public_ip6 = fields.Boolean()
    yggdrasil_ip = fields.Boolean()


class Mount(Data):
    volume_id = fields.String()
    mountpoint = fields.String()


class LogsData(Data):
    stdout = fields.String()
    stderr = fields.String()
    secret_stdout = fields.String()
    secret_stderr = fields.String()


class Logs(Data):
    type = fields.String()
    data = fields.Object(LogsData)


class Stats(Data):
    type = fields.String()
    endpoint = fields.String()


class Capacity(Data):
    cpu = fields.Intger()
    memory = fields.Integer()
    disk_type = fields.Enum(DeviceType)
    disk_size = fields.Integer()


class Container(Data):
    SKIP_CHALLENGE = ["logs", "stats"]

    flist = fields.String()
    hub_url = fields.String()
    entrypoint = fields.String()
    interactive = fields.Boolean()
    env = fields.Typed(dict)
    secret_env = fields.Typed(dict)
    mounts = fields.List(fields.Object(Mount))
    network = fields.Object(Member)
    Capacity = fields.Object(Capacity)

    logs = fields.List(fields.Object(Logs), default=[])
    stats = fields.List(fields.Object(Stats), default=[])


class ContainerResult(Result):
    id = fields.String()
    IPv6 = fields.IPAddress()
    ipv4 = fields.IPAddress()
    ipYgg = fields.String()
