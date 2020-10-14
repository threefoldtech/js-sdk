from jumpscale.packages.marketplace.chats.peertube import Peertube
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class PeertubeAutomated(GedisChatBotPatch, Peertube):
    pass
