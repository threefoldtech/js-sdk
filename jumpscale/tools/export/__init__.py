from jumpscale.loader import j
import tempfile


def _preprocess_exported_file(temp):
    project_path = j.sals.fs.parents(j.sals.fs.realpath(__file__))[2]
    escaped_project_path = project_path.replace("/", "\\\\/")
    project_files = [
        "secureconfig/jumpscale/servers/threebot/threebot/ThreebotServer/default/_package_manager/jumpscale/servers/threebot/threebot/PackageManager/default/data"
    ]
    for pf in project_files:
        j.sals.process.execute(
            ["sed", "-i", f"s/{escaped_project_path}/{{PROJECTPATH}}/g", j.sals.fs.join_paths(temp, pf)]
        )
    root_files = ["secureconfig/jumpscale/tools/startupcmd/startupcmd/StartupCmd/nginx_main/data", "config.toml"]
    home = j.core.dirs.HOMEDIR
    escaped_home = home.replace("/", "\\\\/")
    for rf in root_files:
        j.sals.process.execute(["sed", "-i", f"s/{escaped_home}/{{HOME}}/g", j.sals.fs.join_paths(temp, rf)])


def _postprocess_imported_file(path):
    project_path = j.sals.fs.parents(j.sals.fs.realpath(__file__))[2]
    escaped_project_path = project_path.replace("/", "\\\\/")
    project_files = [
        "secureconfig/jumpscale/servers/threebot/threebot/ThreebotServer/default/_package_manager/jumpscale/servers/threebot/threebot/PackageManager/default/data"
    ]
    for pf in project_files:
        j.sals.process.execute(
            ["sed", "-i", f"s/{{PROJECTPATH}}/{escaped_project_path}/g", j.sals.fs.join_paths(path, pf)]
        )
    root_files = ["secureconfig/jumpscale/tools/startupcmd/startupcmd/StartupCmd/nginx_main/data", "config.toml"]
    home = j.core.dirs.HOMEDIR
    escaped_home = home.replace("/", "\\\\/")
    for rf in root_files:
        j.sals.process.execute(["sed", "-i", f"s/{{HOME}}/{escaped_home}/g", j.sals.fs.join_paths(path, rf)])


def export_threebot_state(output=None):
    home = j.core.dirs.HOMEDIR
    if home is None:
        j.tools.console.printcolors("Error: {RED}Home dir is not found{RESET}")
        return
    config_path = j.sals.fs.join_paths(home, ".config", "jumpscale")
    preprocessing_path = tempfile.mkdtemp()
    tmp_file = tempfile.mkstemp()[1]
    alerts_path = j.sals.fs.join_paths(preprocessing_path, "jumpscale", "logs", "alerts")
    target_file = tmp_file
    try:
        j.sals.fs.copy_tree(config_path, j.sals.fs.join_paths(preprocessing_path, "jumpscale"))
        _preprocess_exported_file(j.sals.fs.join_paths(preprocessing_path, "jumpscale"))
        kube_config = j.sals.fs.join_paths(home, ".kube", "config")
        j.sals.process.execute(["sh", "-c", f"redis-cli HGETALL alerts > {alerts_path}"])
        tf = j.data.tarfile.tarfile.open(target_file, "w")
        tf.add(j.sals.fs.join_paths(preprocessing_path, "jumpscale"), arcname="jumpscale")
        tf.add(kube_config, "config")
        tf.close()
        if output is not None:
            j.sals.fs.rename(target_file, output)
            target_file = output
        j.tools.console.printcolors("Success: {GREEN}Export file created successfully at " + target_file + " {RESET}")
    finally:
        if tmp_file != target_file:
            j.sals.fs.rmtree(tmp_file)
        j.sals.fs.rmtree(preprocessing_path)
    return target_file


def import_threebot_state(file):
    tf = j.data.tarfile.tarfile.open(file, "r")
    home = j.core.dirs.HOMEDIR
    if home is None:
        j.tools.console.printcolors("Error: {RED}Home dir is not found{RESET}")
        return
    kube_config = j.sals.fs.join_paths(home, ".kube", "config")
    config_path = j.sals.fs.join_paths(home, ".config", "jumpscale")
    tmpdir = tempfile.mkdtemp()
    try:
        tf.extractall(tmpdir)
        _postprocess_imported_file(j.sals.fs.join_paths(tmpdir, "jumpscale"))
        j.tools.console.printcolors(
            "Warning: {YELLOW}Please take a backup of ~/.config/jumpscale and ~/.kube/config before continuing{RESET}"
        )
        x = input("Sure you want to override the local jumpscale config at ~/.config/jumpscale [yn]? ")
        if x == "y":
            j.sals.fs.rmtree(config_path)
            j.sals.fs.copy_tree(j.sals.fs.join_paths(tmpdir, "jumpscale"), config_path)
        x = input("Sure you want to override the local kube config at ~/.kube/config [yn]? ")
        if x == "y":
            j.sals.fs.copy_file(j.sals.fs.join_paths(tmpdir, "config"), kube_config)
        tf.close()
    finally:
        j.sals.fs.rmtree(tmpdir)
