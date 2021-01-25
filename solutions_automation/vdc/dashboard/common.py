from solutions_automation.utils.gedispatch import GedisChatBotPatch, DuplicateSolutionNameException


class CommonChatBot(GedisChatBotPatch):
    NAME_MESSAGE = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
    SUB_DOMAIN_CHOICE_MESSAGE = "Select the domain type"
    CUSTOM_SUB_DOMAIN_MESSAGE = r"^Please enter a subdomain to be added to (.*)$"
    FLAVOR_MESSAGE = "Please choose the flavor you want to use (helm chart limits define how much resources the deployed solution will use)"

    QS_BASE = {
        NAME_MESSAGE: "get_name",
        SUB_DOMAIN_CHOICE_MESSAGE: "sub_domain",
        CUSTOM_SUB_DOMAIN_MESSAGE: "custom_sub_domain",
        FLAVOR_MESSAGE: "flavor",
    }

    def get_name(self, msg, *args, **kwargs):
        if self.name_qs == 0:
            self.name_qs = 1
            return self.release_name
        else:
            raise DuplicateSolutionNameException("Release name already exists")
