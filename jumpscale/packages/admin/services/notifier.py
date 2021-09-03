from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService

MAIL_QUEUE = "MAIL_QUEUE"
TELEGRAM_QUEUE = "TELEGRAM_QUEUE"


class Notifier(BackgroundService):
    def __init__(self, interval=60 * 5, *args, **kwargs):
        """
        Notifier service is used to send notifications using different notifications system.
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        self.mail_notifier()

    def mail_notifier(self):
        """Pick mails from redis queue and send them.

        example:
            mail_info = '{"recipients_emails": ["ashraf@codescalers.com"], "sender": "hanafy@codescalers.com", "subject": "Mail Notifier", "message": "Trying mail notifier"}'
            j.core.db.rpush("MAIL_QUEUE", mail_info)
        """
        while True:
            mail_info_json = j.core.db.lpop(MAIL_QUEUE)
            if not mail_info_json:
                break
            try:
                mail_info = j.data.serializers.json.loads(mail_info_json.decode())
                recipients_emails = mail_info["recipients_emails"]
                message = mail_info["message"]
                sender = mail_info["sender"]
                subject = mail_info["subject"]
                self.send_mail(recipients_emails=recipients_emails, subject=subject, message=message, sender=sender)
            except Exception as e:
                j.logger.exception(f"Failed to send mail: {mail_info_json}", exception=e)

    def send_mail(self, recipients_emails, sender, subject, message):
        recipients_emails = recipients_emails or []
        if isinstance(recipients_emails, str):
            recipients_emails = [recipients_emails]
        mail = j.clients.mail.get("mail")
        mail_config = j.core.config.get("EMAIL_SERVER_CONFIG")
        mail.smtp_server = mail_config.get("host")
        mail.smtp_port = mail_config.get("port")
        mail.login = mail_config.get("username")
        mail.password = mail_config.get("password")
        mail.send(recipients_emails, sender=sender, subject=subject, message=message)


service = Notifier()
