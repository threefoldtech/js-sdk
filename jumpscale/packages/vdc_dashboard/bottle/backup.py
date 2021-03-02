from beaker.middleware import SessionMiddleware
from bottle import Bottle, HTTPResponse, request
from jumpscale.loader import j

from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, package_authorized


app = Bottle()


@app.route("/api/backup/list")
@package_authorized("vdc_dashboard")
def list_user_backups() -> str:
    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)
    res = client.execute_native_cmd("velero get backup -o json")
    backups = j.data.serializers.json.loads(res)
    filterd_backups = []
    for bak in backups.get("items"):
        backup_data = {}
        try:
            backup_data["name"] = bak["metadata"]["name"]
            backup_data["expiration"] = j.data.time.get(bak["status"]["expiration"]).timestamp
            backup_data["status"] = bak["status"]["phase"]
            backup_data["start_timestamp"] = j.data.time.get(bak["status"]["startTimestamp"]).timestamp
            backup_data["completion_timestamp"] = j.data.time.get(bak["status"]["completionTimestamp"]).timestamp
            backup_data["errors"] = bak["status"].get("errors", 0)
            backup_data["progress"] = bak["status"]["progress"]
            filterd_backups.append(backup_data)
        except Exception as e:
            j.logger.warning(f"Skipping backup, it has {str(e)} missing.")
    return j.data.serializers.json.dumps({"data": filterd_backups})


@app.route("/api/backup/create", method="POST")
@package_authorized("vdc_dashboard")
def create_backup():
    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)
    time = j.data.time.utcnow().format("YYYYMMDDHHMMSS")
    try:
        client.execute_native_cmd(f"velero create backup config-{time} --include-resources secrets,configmaps")
        client.execute_native_cmd(f'velero create backup vdc-{time} -l "backupType=vdc"')
        return HTTPResponse("Backup created successfully.", status=201, headers={"Content-Type": "application/json"})
    except Exception as e:
        j.logger.warning(f"Failed to create backup due to {str(e)}")
        return HTTPResponse("Failed to create backup.", status=500, headers={"Content-Type": "application/json"})


@app.route("/api/backup/delete", method="POST")
@package_authorized("vdc_dashboard")
def delete_backup():
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    if not name:
        return HTTPResponse(
            "Error: Not all required params was passed.", status=400, headers={"Content-Type": "application/json"},
        )

    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)

    try:
        client.execute_native_cmd(f"velero delete backup {name} --confirm")
        return HTTPResponse("Backup deleted successfully.", status=200, headers={"Content-Type": "application/json"})
    except Exception as e:
        j.logger.warning(f"Failed to delete backup due to {str(e)}")
        return HTTPResponse("Failed to delete backup.", status=500, headers={"Content-Type": "application/json"})


@app.route("/api/backup/restore", method="POST")
@package_authorized("vdc_dashboard")
def restore_backup():
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    if not name:
        return HTTPResponse(
            "Error: Not all required params was passed.", status=400, headers={"Content-Type": "application/json"},
        )

    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)
    time = j.data.time.utcnow().format("YYYYMMDDHHMMSS")

    try:
        client.execute_native_cmd(f"velero create restore restore-{name}-{time} --from-backup {name}")
        return HTTPResponse("Backup restored successfully.", status=200, headers={"Content-Type": "application/json"})
    except Exception as e:
        j.logger.warning(f"Failed to restore backup due to {str(e)}")
        return HTTPResponse("Failed to restore backup.", status=500, headers={"Content-Type": "application/json"})


app = SessionMiddleware(app, SESSION_OPTS)
