from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.peertube import PeertubeDeploy


class PeertubeAutomated(CommonChatBot, PeertubeDeploy):
    pass
