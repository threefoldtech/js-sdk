from jumpscale.packages.tfgrid_solutions.chats.gw4to6 import FourToSixGateway
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class FourToSixGatewayAutomated(GedisChatBotPatch, FourToSixGateway):
    GATEWAY = "Please select a gateway"
    PUBLIC_KEY = "Please enter wireguard public key or leave empty if you want us to generate one for you."
    QS = {GATEWAY: "gateway", PUBLIC_KEY: "public_key"}
