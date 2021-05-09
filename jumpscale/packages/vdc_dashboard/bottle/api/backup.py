from bottle import Bottle, HTTPResponse, request
from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import package_authorized

from .root import app

VDC_BACKUP_PREFIX = "vdc-"
CONFIG_BACKUP_PREFIX = "config-"


def _extract_name(backup):
    if backup["metadata"]["name"].startswith(VDC_BACKUP_PREFIX):
        b = backup["metadata"]["name"][len(VDC_BACKUP_PREFIX) :]
    elif backup["metadata"]["name"].startswith(CONFIG_BACKUP_PREFIX):
        b = backup["metadata"]["name"][len(CONFIG_BACKUP_PREFIX) :]

    return b


def _check_sch_type(backup):
    if backup["metadata"]["labels"].get("velero.io/schedule-name"):
        return {"sch": True, "type": backup["metadata"]["labels"]["velero.io/schedule-name"]}
    else:
        return {"sch": False, "type": ""}


def _list():
    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)
    res = client.execute_native_cmd("velero get backup -o json")
    backups = j.data.serializers.json.loads(res)
    items = backups.get("items")
    items.sort(key=_extract_name)
    filtered_backups = []
    for i in range(0, len(items), 2):
        try:
            backup_1 = items[i]
            backup_2 = items[i + 1]
            backup_data = {}
            backup_1_name = _extract_name(backup_1)
            backup_2_name = _extract_name(backup_2)

            backup_1_type = _check_sch_type(backup_1)
            backup_2_type = _check_sch_type(backup_2)

            if backup_1_type["sch"]:
                backup_data["name"] = f"schedule-{backup_1_name[:len(backup_1_name) -2]}"
                backup_data[f'{backup_1_type["type"]}_backup'] = f'{backup_1_type["type"]}-{backup_1_name}'
                backup_data[f'{backup_2_type["type"]}_backup'] = f'{backup_2_type["type"]}-{backup_2_name}'
            elif backup_1_name == backup_2_name:
                backup_data["name"] = backup_1_name
                backup_data["vdc_backup"] = f"{VDC_BACKUP_PREFIX}{backup_1_name}"
                backup_data["config_backup"] = f"{CONFIG_BACKUP_PREFIX}{backup_1_name}"
            else:
                j.logger.warning(f"Skipping backup.")
                continue

            if backup_1["status"]["phase"] != "Completed":
                backup = backup_1
            else:
                backup = backup_2

            backup_data["expiration"] = j.data.time.get(backup["status"]["expiration"]).timestamp
            backup_data["status"] = backup["status"]["phase"]
            backup_data["start_timestamp"] = j.data.time.get(backup["status"]["startTimestamp"]).timestamp
            backup_data["completion_timestamp"] = j.data.time.get(backup["status"]["completionTimestamp"]).timestamp
            backup_data["errors"] = backup["status"].get("errors", 0)
            backup_data["progress"] = backup["status"]["progress"]
            filtered_backups.append(backup_data)
        except Exception as e:
            j.logger.warning(f"Skipping backup, it has {str(e)} missing.")
    return filtered_backups


@app.route("/api/backup/list")
@package_authorized("vdc_dashboard")
def list_user_backups() -> str:
    filtered_backups = _list()
    return j.data.serializers.json.dumps({"data": filtered_backups})


@app.route("/api/backup/create", method="POST")
@package_authorized("vdc_dashboard")
def create_backup():
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    if not name:
        return HTTPResponse(
            "Error: Not all required params was passed.", status=400, headers={"Content-Type": "application/json"},
        )
    backups = _list()
    for backup in backups:
        if name in backup:
            return HTTPResponse(
                "Please select another name. Already exists", status=409, headers={"Content-Type": "application/json"},
            )
    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)
    try:
        j.logger.info(f"Creating backup with name: {name}")
        client.execute_native_cmd(
            f"velero create backup {CONFIG_BACKUP_PREFIX}{name} --include-resources secrets,configmaps"
        )
        client.execute_native_cmd(f'velero create backup {VDC_BACKUP_PREFIX}{name} -l "backupType=vdc"')
        return HTTPResponse("Backup created successfully.", status=201, headers={"Content-Type": "application/json"})
    except Exception as e:
        j.logger.warning(f"Failed to create backup due to {str(e)}")
        return HTTPResponse("Failed to create backup.", status=500, headers={"Content-Type": "application/json"})


@app.route("/api/backup/delete", method="POST")
@package_authorized("vdc_dashboard")
def delete_backup():
    data = j.data.serializers.json.loads(request.body.read())
    vdc_backup_name = data.get("vdc_backup_name")
    config_backup_name = data.get("config_backup_name")
    if not vdc_backup_name or not config_backup_name:
        return HTTPResponse(
            "Error: Not all required params was passed.", status=400, headers={"Content-Type": "application/json"},
        )

    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)

    try:
        j.logger.info(f"Deleting backup with name: {vdc_backup_name}")
        client.execute_native_cmd(f"velero delete backup {vdc_backup_name} --confirm")
        client.execute_native_cmd(f"velero delete backup {config_backup_name} --confirm")
        return HTTPResponse("Backup deleted successfully.", status=200, headers={"Content-Type": "application/json"})
    except Exception as e:
        j.logger.warning(f"Failed to delete backup due to {str(e)}")
        return HTTPResponse("Failed to delete backup.", status=500, headers={"Content-Type": "application/json"})


@app.route("/api/backup/restore", method="POST")
@package_authorized("vdc_dashboard")
def restore_backup():
    data = j.data.serializers.json.loads(request.body.read())
    vdc_backup_name = data.get("vdc_backup_name")
    config_backup_name = data.get("config_backup_name")
    if not vdc_backup_name or not config_backup_name:
        return HTTPResponse(
            "Error: Not all required params was passed.", status=400, headers={"Content-Type": "application/json"},
        )

    config_path = j.sals.fs.expanduser("~/.kube/config")
    client = j.sals.kubernetes.Manager(config_path=config_path)
    time = j.data.time.utcnow().format("YYYYMMDDHHMMSS")

    try:
        j.logger.info(f"Restoring backup with name: {vdc_backup_name}")
        client.execute_native_cmd(
            f"velero create restore restore-{vdc_backup_name}-{time} --from-backup {vdc_backup_name}"
        )
        client.execute_native_cmd(
            f"velero create restore restore-{config_backup_name}-{time} --from-backup {config_backup_name}"
        )
        return HTTPResponse(
            "Backup restored successfully. It may take a few minutes to reflect.",
            status=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        j.logger.warning(f"Failed to restore backup due to {str(e)}")
        return HTTPResponse("Failed to restore backup.", status=500, headers={"Content-Type": "application/json"})
