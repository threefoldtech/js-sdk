from gedispatch import GedisChatBotPatch
from jumpscale.packages.tfgrid_solutions.chats.four_to_sixgw import FourToSixGateway
from time import time


class FourToSixGatewayAutomated(GedisChatBotPatch, FourToSixGateway):
    GATEWAY = "Please select a gateway"
    PUBLIC_KEY = "Please enter wireguard public key or leave empty if you want us to generate one for you."
    QS = {GATEWAY: "choose_random", PUBLIC_KEY: "public_key"}
