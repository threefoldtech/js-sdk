from jumpscale.loader import j

PYTHON_PACKAGES = [
    "jupyterlab",
    "voila",
    "voila-gridstack",
    "voila-vuetify",
    "matplotlib",
    "ipywidgets",
    "jupyterlab_code_formatter",
]


class notebooks:
    def __init__(self):
        self.notebook_dir = j.sals.fs.join_paths(j.core.dirs.BASEDIR)

    def get_cmd(self, voila=False, base_url=None, ip="127.0.0.1", port=8888):
        if not voila:
            # This needs to be executed in the same process and startup cmds uses exec -a <process-name>
            # so if we used a semicolon, it will seperate the execution
            cmd = "jupyter serverextension enable --py jupyterlab_code_formatter\n"
            cmd += "jupyter lab --no-browser --NotebookApp.allow_remote_access=True --NotebookApp.token=''"
            cmd += f" --NotebookApp.password='' --ip={ip} --port={port} --allow-root"
        else:
            cmd = f"voila --Voila.ip={ip}  --Voila.port={port}"

        if base_url:
            cmd += f" --NotebookApp.base_url={base_url}"
        return cmd

    @property
    def startupcmd(self):
        cmd = j.tools.startupcmd.get("notebooks")
        start_cmd = self.get_cmd(base_url="/notebooks/")
        cmd.start_cmd = start_cmd
        cmd.ports = [8888]
        cmd.save()
        return cmd

    def install(self):
        """Called when package is added
        """
        rc, _, _ = j.sals.process.execute("python -c 'import jupyterlab'")
        if rc:
            for package in PYTHON_PACKAGES:
                j.logger.info(f"Installing {package}...")
                rc, _, err = j.sals.process.execute(f"pip3 install {package}")
                if rc:
                    raise j.exceptions.Runtime(err)

            cmd = """
            jupyter labextension install @jupyter-voila/jupyterlab-preview --no-build
            jupyter labextension install @ryantam626/jupyterlab_code_formatter --no-build
            jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build
            jupyter labextension install voila --no-build

            jupyter lab build  --minimize=False

            jupyter extension enable voila --sys-prefix
            jupyter nbextension install voila --sys-prefix --py
            jupyter nbextension enable voila --sys-prefix --py

            """
            j.logger.info("Installing jupyter labextensions...")
            rc, _, err = j.sals.process.execute(cmd, showout=True)
            if rc:
                raise j.exceptions.Runtime(err)

    def uninstall(self):
        """Called when package is deleted
        """
        rc, _, _ = j.sals.process.execute("python -c 'import jupyterlab'")
        if not rc:
            for package in PYTHON_PACKAGES:
                rc, _, err = j.sals.process.execute(f"pip3 uninstall -y {package}", showout=True)
                if rc:
                    raise j.exceptions.Runtime(err)

    def start(self):
        """Called when threebot is started
        """
        if not self.startupcmd.is_running():
            self.startupcmd.start()

    def stop(self):
        if self.startupcmd.is_running():
            self.startupcmd.stop()
