from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.peertube import Peertube
from time import time


class PeertubeAutomated(GedisChatBotPatch, Peertube):
    pass


test = PeertubeAutomated(
    solution_name="peertube1",
    currency="TFT", 
    expiration=time() + 60 * 15,
    flavor="Silver",
    wg_config="NO", 
    debug=True,
)
