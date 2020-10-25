from jumpscale.packages.marketplace.chats.wiki import WikiDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class WikiAutomated(GedisChatBotPatch, WikiDeploy):
    QS = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}
