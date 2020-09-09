from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.taiga import TaigaDeploy
from time import time


class TaigaAutomated(GedisChatBotPatch, TaigaDeploy):
    NAME_MESSAGE = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
    HOST_EMAIL = "Please add the host e-mail address for your solution."

    SMTP_HOST = "Please add the smtp host example: `smtp.gmail.com`"
    HOST_EMAIL_PASSWORD = "Please add the host e-mail password"
    SECRET_KEY = "Please add a secret key for your solution"
    EXPIRATION_MESSAGE = "Please enter the solution's expiration time"
    CURRENCY_MESSAGE = "Please select the currency you want to pay with."

    QS = {
        NAME_MESSAGE: "get_name",
        HOST_EMAIL: "host_email",
        SMTP_HOST: "smtp_host",
        HOST_EMAIL_PASSWORD: "password",
        SECRET_KEY: "secret",
        EXPIRATION_MESSAGE: "expiration",
        CURRENCY_MESSAGE: "currency",

    }


test = TaigaAutomated(
    solution_name="taiga",
    host_email="", 
    smtp_host= "",
    password= "",
    secret= "",
    currency="TFT", 
    expiration=time() + 60 * 15, 
    wg_config="NO", 
    debug=True,
)
