from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.wiki import WikiDeploy
from time import time


class WikiAutomated(GedisChatBotPatch, WikiDeploy):
    EXPECT = set(["title", "repo", "branch"])

    QS_STR = {"Title": "title", "Repository URL": "repo", "Branch": "branch"}


test = WikiAutomated(
    solution_name="threefoldautomated",
    currency="TFT",
    expiration=time() + 60 * 15,
    title="Threefold",
    repo="https://github.com/threefoldfoundation/info_gridmanual",
    branch="master",
)
