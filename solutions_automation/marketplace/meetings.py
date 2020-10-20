from jumpscale.packages.marketplace.chats.meetings import MeetingsDeploy
from utils.gedispatch import GedisChatBotPatch


class MeetingsAutomated(GedisChatBotPatch, MeetingsDeploy):
    pass
