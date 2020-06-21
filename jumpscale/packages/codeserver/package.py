from jumpscale.god import j


class codeserver:
    def __init__(self):
        self.bin_path = j.sals.fs.join_paths(j.core.dirs.BINDIR, "code-server")
        self._started = False

    @property
    def started(self):
        return self._started

    @property
    def startupcmd(self):
        cmd = j.tools.startupcmd.get("codeserver")
        start_cmd = f"{self.bin_path} --auth none --host 127.0.0.1 -p 8080"
        cmd.start_cmd = start_cmd
        return cmd

    def install(self):
        """Called when package is added
        """
        if not j.sals.fs.exists(self.bin_path):
            raise j.exceptions.NotFound("Code server is not installed")

    def uninstall(self):
        """Called when package is deleted
        """
        pass

    def start(self):
        """Called when threebot is started
        """
        if not self.started:
            self.startupcmd.start()
            self._started = True

    def stop(self):
        if self.started:
            self.startupcmd.stop()
            self._started = False
