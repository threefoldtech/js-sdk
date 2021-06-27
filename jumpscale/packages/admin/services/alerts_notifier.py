from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class AlertsNotifier(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        """Notify the support [escalation_emails] with the hurly alerts count.
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.info("Alerts support notifier service: service started")
        # Get the last hour alerts
        time_now = j.data.time.now()
        alerts = j.tools.alerthandler.find(end_time=time_now.timestamp - 60 * 60)
        # get the host info
        host_name = j.sals.nettools.get_host_name()
        ip_info = j.sals.nettools.get_default_ip_config()
        ip_address = ip_info[-1] if len(ip_info) else ""
        escalation_emails = j.core.config.get("ESCALATION_EMAILS", [])

        if escalation_emails and alerts:
            mail_info = {
                "recipients_emails": escalation_emails,
                "sender": "monitor@threefold.com",
                "subject": f"ALerts report from {host_name}:{ip_address}",
                "message": f"""Last hour, {host_name}:{ip_address} raised {len(alerts)} alerts\nPlease check https://{ip_address}/admin \n{time_now.format('YYYY-MM-DD HH:mm:ss ZZ')}\n""",
            }
            j.core.db.rpush("MAIL_QUEUE", j.data.serializers.json.dumps(mail_info))


service = AlertsNotifier()
