from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.discourse import Discourse
from time import time


class DiscourseAutomated(GedisChatBotPatch, Discourse):
    SMTP_HOST = "SMTP Server Address"
    SMTP_USERNAME = "SMTP Server Username"
    STMP_PASSWORD = "SMTP Server Password"

    QS = {
        SMTP_HOST: "smtp_host",
        SMTP_USERNAME: "stmp_username",
        STMP_PASSWORD: "stmp_password",


    }


test = DiscourseAutomated(
    solution_name="discourse", 
    smtp_host="",
    stmp_username= "",
    stmp_password= "",
    currency="TFT", 
    expiration=time() + 60 * 15, 
    wg_config="NO", debug=True,
)
