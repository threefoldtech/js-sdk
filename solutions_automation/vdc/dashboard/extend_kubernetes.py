from solutions_automation.utils.gedispatch import GedisChatBotPatch
from jumpscale.packages.vdc_dashboard.chats.extend_kubernetes import ExtendKubernetesCluster


class ExtendKubernetesAutomated(GedisChatBotPatch, ExtendKubernetesCluster):
    SIZE_MESSAGE = "Choose the Node size"
    EXISTING_BALANCE_MESSAGE = r"^Do you want to use your existing balance to pay (.*) TFT\? \(This will impact the overall expiration of your plan\)$"

    QS = {SIZE_MESSAGE: "size", EXISTING_BALANCE_MESSAGE: "existing_balance"}
