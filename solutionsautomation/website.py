from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.website import WebsiteDeploy
from time import time


class WebsiteAutomated(GedisChatBotPatch, WebsiteDeploy):
    QS = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}


WebsiteAutomated(
    solution_name="auto",
    currency="TFT",
    expiration=time() + 60 * 15,
    title="Threefold",
    repo="https://github.com/xmonader/www_incubaid",
    branch="development",
    wg_config="NO",
    debug=True,
)
