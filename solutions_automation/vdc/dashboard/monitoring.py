from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.monitoringstack import InstallMonitoringStack


class MonitoringStackAutomated(CommonChatBot, InstallMonitoringStack):
    pass
