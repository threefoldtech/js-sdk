import random

from jumpscale.packages.tfgrid_solutions.chats.exposed import SolutionExpose
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class SolutionExposeDeployAutomated(GedisChatBotPatch, SolutionExpose):
    TYPE = "Please choose the solution type"
    SOLUTION_TO_EXPOSE = "Please choose the solution to expose"
    TLS_PORT = "Which tls port you want to expose"
    PORT_EXPOSE = "Which port you want to expose"
    DOMAIN = "Please choose the domain you wish to use"
    SUB_DOMAIN = r"^Please specify the sub domain name you wish to bind to. will .*"
    PROXY_TYPE = "Select how you want to expose your solution (TRC forwards the traffic as is to the specified HTTP/HTTPS ports while NGINX reverse proxies the HTTP/HTTPS requests to an HTTP port)"
    FORCE_HTTPS = "Do you want to force HTTPS?"

    QS = {
        TYPE: "type",
        SOLUTION_TO_EXPOSE: "solution_to_expose",
        TLS_PORT: "tls_port",
        PORT_EXPOSE: "port",
        DOMAIN: "domain",
        SUB_DOMAIN: "sub_domain",
        PROXY_TYPE: "proxy_type",
        FORCE_HTTPS: "force_https",
    }

    # to ignorE Custom Domain option
    def choose_random(self, msg, options, *args, **kwargs):
        if "Custom Domain" in options:
            options.pop()
        return random.choice(options)
