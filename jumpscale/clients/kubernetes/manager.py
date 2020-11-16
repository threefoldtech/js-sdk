from jumpscale.loader import j
from jumpscale.clients.base import Client


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


class Manager(Client):
    """SAL for kubernetes"""

    def __init__(self, config_path=f"{j.core.dirs.HOMEDIR}/.kube/config", *args, **kwargs):
        """constructor for kubernetes class

        Args:
            config_path (str, optional): path to kubeconfig. Defaults to "~/.kube/config".
        """
        super().__init__(*args, **kwargs)
        if not j.sals.fs.exists(config_path) or not j.sals.fs.is_file(config_path):
            raise j.exceptions.NotFound(f"No such file {config_path}")
        self.config_path = config_path

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
        rc, out, err = j.sals.process.execute(f"helm --kubeconfig {self.config_path} repo add {name} {url}")
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to add repo: {name} with url:{url}, error was {err}")
        return out

    @helm_required
    def update_helm_repo(self):
        """Update helm repo

        Raises:
            j.exceptions.Runtime: in case the command failed to execute

        Returns:
            str: output of the helm command
        """
        rc, out, err = j.sals.process.execute(f"helm --kubeconfig {self.config_path} repo update")
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to update repo, error was {err}")
        return out

    @helm_required
    def install_chart(self, release, chart_name, config=None):
        """deployes a helm chart

        Args:
            release (str): name of the relase to be deployed
            chart_name (str): the name of the chart you need to deploy

        Raises:
            j.exceptions.Runtime: in case the helm command failed to execute

        Returns:
            str: output of the helm command
        """
        cmd = f"helm --kubeconfig {self.config_path} install {release} {chart_name}"
        if config:
            cmd += "".join([f" --set {key}={value} " for key, value in config.items()]).strip()

        rc, out, err = j.sals.process.execute(cmd)
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to deploy chart {chart_name}, error was {err}")
        return out

    @helm_required
    def delete_deployed_release(self, release):
        """deletes deployed helm release

        Args:
            release (str): name of the release you want to remove

        Raises:
            j.exceptions.Runtime: in case the helm command failed to execute

        Returns:
            str: output of the helm command
        """
        rc, out, err = j.sals.process.execute(f"helm --kubeconfig {self.config_path} delete {release}")
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to deploy chart {release} , error was {err}")
        return out

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
        rc, out, err = j.sals.process.execute(cmd)
        if rc != 0:
            raise j.exceptions.Runtime(f"Failed to execute: {cmd}, error was {err}")
        return out
