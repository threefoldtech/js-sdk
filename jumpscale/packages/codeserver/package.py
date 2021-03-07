from jumpscale.loader import j
import os


class codeserver:
    def __init__(self):
        self.bin_path = j.sals.fs.join_paths(j.core.dirs.BINDIR, "code-server")
        self.script_path = j.sals.fs.join_paths(os.path.dirname(__file__), "codeserver_install.sh")
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
            rc, out, err = j.sals.process.execute(f"chmod +x {self.script_path}; {self.script_path}")
            if rc:
                raise j.exceptions.Runtime(err)

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
