from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.wiki import WikiDeploy


class WikiAutomated(CommonChatBot, WikiDeploy):
    TITLE_MESSAGE = "Title"
    URL_MESSAGE = "Repository URL"
    BRANCH_MESSAGE = "Branch"
    SOURCE_DIR_MESSAGE = "Source directory"

    QS = {TITLE_MESSAGE: "title", URL_MESSAGE: "url", BRANCH_MESSAGE: "branch", SOURCE_DIR_MESSAGE: "src_dir"}
