from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.website import WebsiteDeploy


class WebsiteAutomated(CommonChatBot, WebsiteDeploy):
    TITLE_MESSAGE = "Title"
    URL_MESSAGE = "Repository URL"
    BRANCH_MESSAGE = "Branch"

    QS = {TITLE_MESSAGE: "title", URL_MESSAGE: "url", BRANCH_MESSAGE: "branch"}
