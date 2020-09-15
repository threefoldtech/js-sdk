from gedispatch import GedisChatBotPatch
from jumpscale.packages.tfgrid_solutions.chats.delegated_domain import DomainDelegation


class DomainDelegationAutomated(GedisChatBotPatch, DomainDelegation):
    GATEWAY = "Please select a gateway"
    DOMAIN_NAME = "Please enter a domain name to delegate"

    QS = {
        GATEWAY: "choose_random",
        DOMAIN_NAME: "get_name",
    }
