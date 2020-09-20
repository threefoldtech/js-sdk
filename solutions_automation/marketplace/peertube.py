from jumpscale.packages.marketplace.chats.peertube import Peertube
from utils.gedispatch import GedisChatBotPatch


class PeertubeAutomated(GedisChatBotPatch, Peertube):
    pass
