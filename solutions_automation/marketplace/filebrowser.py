from jumpscale.packages.marketplace.chats.filebrowser import FilebrowserDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class FilebrowserAutomated(GedisChatBotPatch, FilebrowserDeploy):
    DOCUMENTSERVER_URL = "Please add the url to a documentserver"

    QS = {DOCUMENTSERVER_URL: "https://office.jimber.org"}
