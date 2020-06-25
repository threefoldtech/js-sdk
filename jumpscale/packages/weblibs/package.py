from jumpscale.god import j


class weblibs:
    def __init__(self):
        self.url = "https://github.com/threefoldtech/jumpscaleX_weblibs"
        self.path = j.sals.fs.join_paths(j.core.dirs.CODEDIR, "github")
        self.branch = "development"

    def install(self):
        """Called when package is added
        """
        if not j.sals.fs.exists(j.sals.fs.join_paths(self.path, "jumpscaleX_weblibs")):
            retries = 5
            while retries:
                try:
                    j.tools.git.clone_repo(url=self.url, dest=self.path, branch_or_tag=self.branch)
                    break
                except Exception:
                    if retries == 1:
                        raise j.exceptions.Timeout("Clone weblibs repo failed")
                    retries = retries - 1

    def uninstall(self):
        """Called when package is deleted
        """
        pass

    def start(self):
        """Called when threebot is started
        """
        pass

    def stop(self):
        pass
