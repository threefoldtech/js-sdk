from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.peertube import Peertube


class PeertubeAutomated(GedisChatBotPatch, Peertube):
    pass
