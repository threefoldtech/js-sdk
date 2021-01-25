from solutions_automation.utils.gedispatch import GedisChatBotPatch
from jumpscale.packages.vdc_dashboard.chats.extend_kubernetes import ExtendKubernetesCluster


class ExtendKubernetesAutomated(GedisChatBotPatch, ExtendKubernetesCluster):
    SIZE_MESSAGE = "Choose the Node size"

    QS = {SIZE_MESSAGE: "size"}
