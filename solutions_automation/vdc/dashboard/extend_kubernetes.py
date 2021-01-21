from solutions_automation.utils.gedispatch import GedisChatBotPatch
from jumpscale.packages.vdc_dashboard.chats.extend_kubernetes import ExtendKubernetesCluster


class ExtendKubernetesAutomated(GedisChatBotPatch, ExtendKubernetesCluster):
    FLAVOR_MESSAGE = "Choose the Node size"

    QS = {FLAVOR_MESSAGE: "flavor"}
