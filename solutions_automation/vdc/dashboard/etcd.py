from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.etcd import EtcdDeploy


class EtcdAutomated(CommonChatBot, EtcdDeploy):
    pass
