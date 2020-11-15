from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method

from shlex import quote
from kubernetes import client, config


class HelmChart(BaseActor):
    @actor_method
    def load_cluster_config(self, path: str) -> str:
        """
            Loads kubernetes cluster config
        """
        # TODO can be replaced with export or added in executer env variable(KUBECONFIG)
        config_path = path or j.sals.fs.join_paths(j.core.dirs.HOMEDIR, ".kube", "config")

        if j.sals.fs.exists(config_path):
            config.load_kube_config(config_file=config_path)
            return j.data.serializers.json.dumps("OK")
        else:
            return j.data.serializers.json.dumps("Path does not exist")

    @actor_method
    def install_helm_chart(
        self, repo_name: str, repo_url: str, instance_name: str, chart_name: str, config: dict = None
    ) -> str:
        config = config or {}

        cmd = f"helm repo add {name} {repo_url}"
        j.core.executors.run_local(quote(cmd))
        cmd = f"helm install {instance_name} {chart_name}"
        cmd += "".join([f" --set {key}={value} " for key, value in config.items()]).strip()

        j.core.executors.run_local(quote(cmd))


Actor = HelmChart
