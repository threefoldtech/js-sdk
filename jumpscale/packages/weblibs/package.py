from jumpscale.loader import j


class weblibs:
    def __init__(self):
        self.url = "https://github.com/threefoldtech/jumpscaleX_weblibs"
        self.path = j.sals.fs.join_paths(j.core.dirs.CODEDIR, "github")
        self.branch = "development"

    def install(self):
        """Called when package is added
        """
        if not j.sals.fs.exists(j.sals.fs.join_paths(self.path, "jumpscaleX_weblibs")):
            retries = 3
            while retries:
                try:
                    j.tools.git.clone_repo(url=self.url, dest=self.path, branch_or_tag=self.branch, depth=1)
                    return
                except Exception as e:
                    retries -= 1
                    msg = str(e)
                    # check if error not lost internet connection don't try again
                    if not retries or msg.find("Could not resolve host") == -1:
                        raise e

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
