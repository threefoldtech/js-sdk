from gitea import GiteaAutomated
from cryptpad import CryppadAutomated
from wiki import CryppadAutomated
from mattermost import mattermostAutomated
from ubuntu import UbuntuAutomated


class Factory:
    def deploy_gitea(self, solution_name, currency, expiration, wg_config, debug=True):
        return GiteaAutomated(
            solution_name=solution_name, currency=currency, expiration=expiration, wg_config=wg_config, debug=debug
        )

    def deploy_ubuntu(
        self,
        solution_name,
        version="ubuntu-18.04",
        cpu=1,
        memory=1024,
        disk_size=256,
        disk_type="SSD",
        log="NO",
        ssh="~/.ssh/id_rsa.pub",
        ipv6="NO",
        node_automatic="YES",
        node="choose_random",
        ipv4="choose_random",
        network="choose_random",
        pool="choose_random",
        debug=True,
    ):
        return UbuntuAutomated(
            solution_name,
            version=version,
            cpu=cpu,
            memory=memory,
            disk_size=disk_size,
            disk_type=disk_type,
            log=log,
            ssh=ssh,
            ipv6=ipv6,
            node_automatic=node_automatic,
            node=node,
            ipv4=ipv4,
            network=network,
            pool=pool,
            debug=True,
        )

    def deploy_cryptpad(self, solution_name, currency, expiration, wg_config, debug=True):
        return CryppadAutomated(
            solution_name=solution_name, currency=currency, expiration=expiration, wg_config=wg_config, debug=debug
        )
