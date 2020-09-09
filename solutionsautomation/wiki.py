from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.wiki import WikiDeploy


class WikiAutomated(GedisChatBotPatch, WikiDeploy):
    QS = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}
