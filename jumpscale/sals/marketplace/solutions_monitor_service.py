import time
import requests

from jumpscale.loader import j
from jumpscale.core.base import StoredFactory
from jumpscale.clients.explorer.models import NextAction

from .models import DeployStatus
from .apps_chatflow import BACKUP_MODEL

ENDPOINT = ":8881/api/health"


def _check_deployment_status(workload_id):
    workload = j.sals.zos.workloads.get(workload_id)
    if workload.info.next_action != NextAction.DEPLOY:
        return DeployStatus.EXPIRED


def _check_health_status(endpoint):
    health_state = "ERROR"
    try:
        health_state = requests.get(endpoint).json().get("status")
    except Exception as e:
        j.log.error(f"Connection Error\n{str(e)}")
    return health_state


def _redeploy(solution):
    # TODO: DEPLOYMENT FAILURE
    pass


def main():
    monitored_solutions = BACKUP_MODEL.list_all()
    while True:
        for name in monitored_solutions:
            solution = BACKUP_MODEL.get(name)
            domain = solution.get(name).domain
            endpoint = f"{domain}{ENDPOINT}"
            workload_id = solution.get(name).workload_id

            # Check deployment & reachability status
            last_status = solution.status
            last_action_time = solution.action_time

            if _check_deployment_status(workload_id) == DeployStatus.EXPIRED:
                continue

            if last_status == DeployStatus.DEPLOYING:
                if j.data.time.utcnow().timestamp - last_action_time >= 15 * 60:
                    solution.status = DeployStatus.DEPLOY
                else:
                    continue

            if not j.sals.nettools.check_url_reachabel(domain) or not _check_health_status(endpoint):
                # hardware failure / service failure
                if last_status == DeployStatus.FAILURE:
                    if j.data.time.utcnow().timestamp - last_action_time >= 15 * 60:
                        _redeploy(solution)
                        solution.action_time = j.data.time.utcnow().timestamp
                        solution.status = DeployStatus.DEPLOYING
                        solution.save()
                    else:
                        continue
                else:
                    solution.action_time = j.data.time.utcnow().timestamp
                    solution.status = DeployStatus.FAILURE
                    solution.save()
                    continue

            if last_status == DeployStatus.DEPLOY:
                solution.action_time = j.data.time.utcnow().timestamp
                solution.status = DeployStatus.DEPLOY
                solution.save()
        time.sleep(5 * 60)


if __name__ == "__main__":
    main()
