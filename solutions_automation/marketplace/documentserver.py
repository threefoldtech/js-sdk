from jumpscale.packages.marketplace.chats.documentserver import DocumentserverDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class DocumentserverAutomated(GedisChatBotPatch, DocumentserverDeploy):
    pass
