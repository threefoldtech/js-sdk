from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.website import WebsiteDeploy


class WebsiteAutomated(GedisChatBotPatch, WebsiteDeploy):
    QS = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}
