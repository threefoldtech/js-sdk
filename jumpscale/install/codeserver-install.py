from jumpscale.core.base import StoredFactory
from jumpscale.servers.threebot.threebot import ThreebotServer
from jumpscale.loader import j

factory = StoredFactory(ThreebotServer)
threebot = factory.get("default")
threebot.packages.add(j.sals.fs.parent(j.packages.codeserver.__file__))
threebot.save()
