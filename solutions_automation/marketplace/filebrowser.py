from jumpscale.packages.marketplace.chats.filebrowser import FilebrowserDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class FilebrowserAutomated(GedisChatBotPatch, FilebrowserDeploy):
    pass
