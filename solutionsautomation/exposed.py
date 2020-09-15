from gedispatch import GedisChatBotPatch
from jumpscale.packages.tfgrid_solutions.chats.exposed import SolutionExpose
import random


class SolutionExposeDeployAutomated(GedisChatBotPatch, SolutionExpose):
    SOLUTION_TYPE = "Please choose the solution type"
    SOLUTION_EXPOSE = "Please choose the solution to expose"
    TLS_PORT = "Which tls port you want to expose"
    PORT_EXPOSE = "Which port you want to expose"
    DOMAIN = "Please choose the domain you wish to use"
    SUB_DOMAIN = r"^Please specify the sub domain name you wish to bind to. will .*"

    QS = {
        SOLUTION_TYPE: "type",
        SOLUTION_EXPOSE: "choose_random",
        TLS_PORT: "tls_port",
        PORT_EXPOSE: "port_expose",
        DOMAIN: "choose_domain_random",
        SUB_DOMAIN: "sub_domain",
    }

    # to ignor Custom Domain option
    def choose_domain_random(self, msg, options, *args, **kwargs):
        options.pop()
        return random.choice(options)
