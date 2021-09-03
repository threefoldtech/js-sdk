from jumpscale.packages.vdc.chats.new_vdc import VCD_DEPLOYING_INSTANCES
from jumpscale.loader import j


class vdc:
    def start(self, **kwargs):
        # clear the deploying instances from redis
        j.core.db.delete(VCD_DEPLOYING_INSTANCES)
