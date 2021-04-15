from jumpscale.loader import j
import tempfile


def export_threebot_state(output=None):
    home = j.core.dirs.HOMEDIR
    if home is None:
        j.tools.console.printcolors("Error: {RED}Home dir is not found{RESET}")
        return
    config_path = j.sals.fs.join_paths(home, ".config", "jumpscale")
    output_tmp_file = tempfile.mkstemp()[1]
    alerts_tmp_file = tempfile.mkstemp()[1]
    alerts_path = j.sals.fs.join_paths("jumpscale", "logs", "alerts")
    target_file = output_tmp_file
    try:
        j.sals.process.execute(["sh", "-c", f"redis-cli HGETALL alerts > {alerts_tmp_file}"])
        tf = j.data.tarfile.tarfile.open(target_file, "w")
        tf.add(config_path, arcname="jumpscale")
        tf.add(alerts_tmp_file, arcname=alerts_path)
        tf.close()
        if output is not None:
            j.sals.fs.rename(target_file, output)
            target_file = output
        j.tools.console.printcolors("Success: {GREEN}Export file created successfully at " + target_file + " {RESET}")
    finally:
        if output_tmp_file != target_file:
            j.sals.fs.rmtree(output_tmp_file)
        j.sals.fs.rmtree(alerts_tmp_file)
    return target_file
