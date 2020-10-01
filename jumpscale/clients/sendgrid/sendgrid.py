import base64
import os
import io
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment
from python_http_client.exceptions import HTTPError
from jumpscale.loader import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields


class SendGridClient(Client):
    apikey = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_attachment(self, filepath, typ="application/pdf"):
        """
        Returns a valid sendgrid attachment from typical attachment object.
        """
        data = io.BytesIO()
        with open(filepath, "rb") as f:
            while True:
                d = f.read(2 ** 20)
                if not d:
                    break
                data.write(d)
        data.seek(0)
        attachment = sendgrid.Attachment()
        attachment.file_content = j.data.serializers.base64.encode(data.read()).decode()
        attachment.file_type = typ
        attachment.file_name = os.path.basename(filepath)
        attachment.disposition = "attachment"
        return attachment

    def send(self, sender, subject, html_content="<strong>Email</strong>", recipients=None, attachments=None):
        recipients = recipients or []
        attachments = attachments or []
        recipients = list(set(recipients))
        mail = Mail(from_email=sender, to_emails=recipients, subject=subject, html_content=html_content)
        for at in attachments:
            mail.add_attachment(at)
        try:
            sg = sendgrid.SendGridAPIClient(self.apikey)
            # response=sg.send(mail)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except HTTPError as e:
            raise e

