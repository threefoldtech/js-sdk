import random

from jumpscale.packages.tfgrid_solutions.chats.exposed import SolutionExpose
from utils.gedispatch import GedisChatBotPatch


class SolutionExposeDeployAutomated(GedisChatBotPatch, SolutionExpose):
    SOLUTION_TYPE = "Please choose the solution type"
    SOLUTION_TO_EXPOSE = "Please choose the solution to expose"
    TLS_PORT = "Which tls port you want to expose"
    PORT_EXPOSE = "Which port you want to expose"
    DOMAIN = "Please choose the domain you wish to use"
    SUB_DOMAIN = r"^Please specify the sub domain name you wish to bind to. will .*"

    QS = {
        SOLUTION_TYPE: "solution_type",
        SOLUTION_TO_EXPOSE: "solution_to_expose",
        TLS_PORT: "tls_port",
        PORT_EXPOSE: "port",
        DOMAIN: "domain",
        SUB_DOMAIN: "sub_domain",
    }

    # to ignorE Custom Domain option
    def choose_random(self, msg, options, *args, **kwargs):
        if "Custom Domain" in options:
            options.pop()
        return random.choice(options)
