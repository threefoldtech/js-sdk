from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.blog import BlogDeploy
from time import time


class BlogAutomated(GedisChatBotPatch, BlogDeploy):
    QS = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}


BlogAutomated(
    solution_name="auto",
    currency="TFT",
    expiration=time() + 60 * 15,
    title="Threefold",
    repo="https://github.com/threefoldfoundation/blog_threefold",
    branch="development",
    wg_config="NO",
    debug=True,
)
