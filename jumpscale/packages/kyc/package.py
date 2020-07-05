from jumpscale.loader import j
import os


class kyc:
    def __init__(self):
        # Make sure zdb is started
        cmd = j.tools.startupcmd.get("zdbserver")
        self.zdb_path = j.sals.fs.join_paths(j.core.dirs.BINDIR, "zdb")
        self.bcdb_path = j.sals.fs.join_paths(j.core.dirs.BINDIR, "bcdb")
        self._started = False

    @property
    def started(self):
        return self._started

    @property
    def _zdb_startupcmd(self):
        cmd = j.tools.startupcmd.get("zdbserver")
        cmd.start_cmd = f"{self.zdb_path} --mode seq"
        return cmd

    @property
    def _bcdb_startupcmd(self):
        cmd = j.tools.startupcmd.get("bcdbserver")
        tid = j.core.identity.me.tid
        seed = j.core.identity.me.words
        cmd.start_cmd = f"{self.bcdb_path} --threebot-id {tid} --seed '{seed}'"
        return cmd

    def install(self):
        """Called when package is added
        """
        pass

    def uninstall(self):
        """Called when package is deleted
        """
        pass

    def start(self):
        """Called when threebot is started
        """
        if not self.started:

            self._zdb_startupcmd.start()

            self._bcdb_startupcmd.start()
            self._started = True

    def stop(self):
        if self.started:
            self._zdb_startupcmd.stop()
            self._bcdb_startupcmd.stop()
            self._started = False
