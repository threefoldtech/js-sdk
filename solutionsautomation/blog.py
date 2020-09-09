from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.blog import BlogDeploy


class BlogAutomated(GedisChatBotPatch, BlogDeploy):
    QS = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}
