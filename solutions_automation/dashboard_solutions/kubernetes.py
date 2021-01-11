from jumpscale.packages.tfgrid_solutions.chats.kubernetes import KubernetesDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class KubernetesAutomated(GedisChatBotPatch, KubernetesDeploy):
    NAME_MESSAGE = "Please enter a name for your workload (Can be used to prepare domain for you and needed to track your solution on the grid)"
    NODE_SIZE_MESSAGE = "Choose the size of your nodes"
    WORKERS_NUM_MESSAGE = "Please specify the number of worker nodes"
    NETWORK_MESSAGE = "Please select a network"
    SSH_MESSAGE = "Please upload your public SSH key to be able to access the depolyed container via ssh"
    SECRET_MESSAGE = "Please add the cluster secret"
    IP_MASTER_MESSAGE = "Please choose IP Address for Master node"
    IP_SLAVE_MESSAGE = r"Please choose IP Address for Slave node (.*)"
    POOL_MESSAGE = "Please select the pools you wish to distribute you Kubernetes nodes on"

    QS = {
        # strs
        NAME_MESSAGE: "get_name",
        SSH_MESSAGE: "ssh",
        SECRET_MESSAGE: "secret",
        # ints
        WORKERS_NUM_MESSAGE: "workernodes",
        # single choice
        NODE_SIZE_MESSAGE: "size",
        NETWORK_MESSAGE: "network",
        IP_MASTER_MESSAGE: "choose_random",
        IP_SLAVE_MESSAGE: "choose_random",
        # multi choice
        POOL_MESSAGE: "pools",
    }

    def multi_list_choice(self, msg, options, *args, **kwargs):
        selected = self.fetch_param(msg, *args, **kwargs)
        if options:
            for m in options:
                if str(selected) in m:
                    return [m]
        return [selected]
