from jumpscale.packages.marketplace.chats.meetings import MeetingsDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class MeetingsAutomated(GedisChatBotPatch, MeetingsDeploy):
    pass
