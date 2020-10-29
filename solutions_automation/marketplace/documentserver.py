from jumpscale.packages.marketplace.chats.documentserver import DocumentserverDeploy
from utils.gedispatch import GedisChatBotPatch


class DocumentserverAutomated(GedisChatBotPatch, DocumentserverDeploy):
    pass
