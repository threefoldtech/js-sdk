from shlex import quote
from jumpscale.loader import j


def is_helm_installed():
    """Checks if helm is installed on system or not

    Returns:
        bool: True if helm is installed, False otherwise
    """
    rc, _, _ = j.sals.process.execute("helm version")
    return rc == 0


def helm_required(method):
    """a decorator to check if helm is installed or not

    Args:
        method (func): function to be decorated
    """

    def wrapper(self, *args, **kwargs):
        if not is_helm_installed():
            raise j.exceptions.NotFound("Helm is not installed on the system")
        return method(self, *args, **kwargs)

    return wrapper


class Manager:
    """SAL for kubernetes"""

    def __init__(self, config_path=f"{j.core.dirs.HOMEDIR}/.kube/config"):
        """constructor for kubernetes class

        Args:
            config_path (str, optional): path to kubeconfig. Defaults to "~/.kube/config".
        """
        if not j.sals.fs.exists(config_path) or not j.sals.fs.is_file(config_path):
            raise j.exceptions.NotFound(f"No such file {config_path}")
        self.config_path = config_path

    @staticmethod
    def _execute(cmd):
        j.logger.debug(f"kubernetes manager: {cmd}")
        return j.sals.process.execute(cmd)

    @helm_required
    def update_repos(self):
        """Update helm repos

        Returns:
            str: output of the helm command
        """
        rc, out, err = self._execute(f"helm --kubeconfig {self.config_path} repo update")
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to update repos error was {err}")
        return out

    @helm_required
    def upgrade_release(self, release, repo, namespace, yaml_config):
        """Update helm repos

        Returns:
            str: output of the helm command
        """
        rc, out, err = self._execute(
            f"helm --kubeconfig {self.config_path} upgrade {release} {repo} --namespace {namespace} -f <(echo -e '{yaml_config}')"
        )
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to upgrade release error was {err}")
        return out

    @helm_required
    def add_helm_repo(self, name, url):
        """Add helm repo

        Args:
            name (str): name of the repo to be added
            url (str): url of the repo to be added

        Raises:
            j.exceptions.Runtime: in case the command failed to execute

        Returns:
            str: output of the helm command
        """
        rc, out, err = self._execute(f"helm --kubeconfig {self.config_path} repo add {name} {url}")
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to add repo: {name} with url:{url}, error was {err}")
        return out

    @helm_required
    def install_chart(self, release, chart_name, namespace="default", extra_config=None, chart_values_file=None):
        """deployes a helm chart

        Args:
            release (str): name of the release to be deployed
            chart_name (str): the name of the chart you need to deploy
            extra_config: dict containing extra paramters passed to install command with --set

        Raises:
            j.exceptions.Runtime: in case the helm command failed to execute

        Returns:
            str: output of the helm command
        """
        extra_config = extra_config or {}
        params = ""
        for key, arg in extra_config.items():
            params += f" --set {key}={quote(arg)}"
        cmd = f"helm --kubeconfig {self.config_path} --namespace {namespace} install {release} {chart_name} {params}"
        if chart_values_file:
            cmd += f" -f {chart_values_file}"
        rc, out, err = self._execute(cmd)
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to deploy chart {chart_name}, error was {err}")
        return out

    def get_k8s_sshclient(self, instance, host, private_key_path="/root/.ssh/id_rsa", user="rancher"):
        """Get sshclient for k8s
        Arg:
            instance(str): name of the instance
            host(str): the host is used to connect to
            private_key_path(str): the path of private key to use during ssh
            user(str): the name of user will be used during ssh
        Returns:
            ssh_client(obj): object of ssh client to be used in remote execution
        """
        ssh_key = j.clients.sshkey.get(instance)
        ssh_key.private_key_path = private_key_path
        ssh_key.load_from_file_system()
        ssh_client = j.clients.sshclient.get(instance, user=user, host=host, sshkey=instance)
        return ssh_client

    @helm_required
    def delete_deployed_release(self, release, namespace="default", vdc_instance=None):
        """deletes deployed helm release

        Args:
            release (str): name of the release you want to remove

        Raises:
            j.exceptions.Runtime: in case the helm command failed to execute

        Returns:
            str: output of the helm command
        """
        # Getting k8s master IP
        if vdc_instance:
            for node in vdc_instance.kubernetes:
                if node.role.value == "master":
                    k8s_master_ip = node.ip_address
                    break
            else:
                raise j.exceptions.Runtime(f"Failed to get the master ip for this release {release}")

        rc, out, err = self._execute(f"helm --kubeconfig {self.config_path} --namespace {namespace} delete {release}")
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to deploy chart {release} , error was {err}")

        # Validate service running
        ssh_client = self.get_k8s_sshclient(instance=release, host=k8s_master_ip)
        rc, out, err = ssh_client.sshclient.run(f"sudo rc-service -l | grep -i '^{release}-socat-'", warn=True,)

        if rc == 0:
            results = out.split("\n")
            for result in results:
                rc, out, err = ssh_client.sshclient.run(
                    f"sudo rc-service -s {result.strip()} stop && sudo rm -f /etc/init.d/{result.strip()}", warn=True,
                )

        return out

    @helm_required
    def list_deployed_releases(self, namespace="default"):
        """list deployed helm releases

        Returns:
            list: output of the helm command as dicts
        """
        rc, out, err = self._execute(f"helm --kubeconfig {self.config_path} --namespace {namespace} list -o json")
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to list charts, error was {err}")
        return j.data.serializers.json.loads(out)

    @helm_required
    def get_deployed_release(self, release_name):
        rc, out, err = self._execute(f"helm --kubeconfig {self.config_path} get values {release_name}")
        if rc != 0:
            return None
        return j.data.serializers.yaml.loads(out)

    @helm_required
    def execute_native_cmd(self, cmd):
        """execute a native kubectl/helm command

        Args:
            cmd (str): the command you want to execute

        Raises:
            j.exceptions.Runtime: in case the command failed

        Returns:
            str: output of the kubectl/helm command
        """
        cmd = f"{cmd} --kubeconfig {self.config_path}"
        rc, out, err = self._execute(cmd)
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to execute: {cmd}, error was {err}")
        return out

    @helm_required
    def get_helm_chart_user_values(self, release, namespace="default"):
        """Get helm chart user supplied values that were supplied during installation of the chart(using --set)

        Args:
            release (str): name of the relase to get chart values for
        Raises:
            j.exceptions.Runtime: in case the command failed to execute

        Returns:
            str: output of the helm command
        """
        rc, out, err = self._execute(
            f"helm get values --kubeconfig {self.config_path} --namespace={namespace} {release} -o json"
        )
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to list calues of helm chart, error was {err}")
        return out

    @helm_required
    def list_helm_repos(self):
        """List helm repos
        Raises:
            j.exceptions.Runtime: in case the command failed to execute
        Returns:
            list: list of added repos [{"name":"stable","url":"https://charts.helm.sh/stable"}]
        """
        cmd = f"helm repo list -o json --kubeconfig {self.config_path}"
        rc, out, err = self._execute(cmd)
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to execute: {cmd}, error was {err}")
        return j.data.serializers.json.loads(out)
