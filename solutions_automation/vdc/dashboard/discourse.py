from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.discourse import DiscourseDeploy


class DiscourseAutomated(CommonChatBot, DiscourseDeploy):
    pass
