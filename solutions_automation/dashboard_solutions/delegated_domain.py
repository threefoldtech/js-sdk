from jumpscale.packages.tfgrid_solutions.chats.delegated_domain import DomainDelegation
from utils.gedispatch import GedisChatBotPatch


class DomainDelegationAutomated(GedisChatBotPatch, DomainDelegation):
    GATEWAY = "Please select a gateway"
    DOMAIN = "Please enter a domain name to delegate"

    QS = {
        GATEWAY: "gatway",
        DOMAIN: "domain",
    }
