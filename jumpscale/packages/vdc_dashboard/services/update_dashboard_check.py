from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.tools.notificationsqueue.queue import LEVEL
from jumpscale.loader import j


class UpdateDashboardCheck(BackgroundService):
    def __init__(self, interval=60 * 60 * 2, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.sals.process.execute(f"git fetch -a")
        # get the HEAD commit hash
        _, HEAD, _ = j.sals.process.execute("git rev-parse HEAD")
        # get the remote commit hash
        _, branch, _ = j.sals.process.execute(f"git branch --show-current")
        _, remote_HEAD, _ = j.sals.process.execute(f"git rev-parse origin/{branch}")

        if HEAD != remote_HEAD:
            j.logger.info(f"UPDATE_DASHBOARD_CHECK: New update for the dashboard is available")
            j.tools.notificationsqueue.push(
                "New update for the dashboard is available, please update it from the menu bar",
                category="Dashboard",
                level=LEVEL.INFO,
            )


service = UpdateDashboardCheck()
