from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.kubeapps import KubeappsDeploy


class KubeappsAutomated(CommonChatBot, KubeappsDeploy):
    pass
