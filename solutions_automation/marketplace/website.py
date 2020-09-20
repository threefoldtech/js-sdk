from jumpscale.packages.marketplace.chats.website import WebsiteDeploy
from utils.gedispatch import GedisChatBotPatch


class WebsiteAutomated(GedisChatBotPatch, WebsiteDeploy):
    QS = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}
