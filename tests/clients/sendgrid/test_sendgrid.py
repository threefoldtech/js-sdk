import email
import imaplib
import os
import string

import gevent
import pytest
from jumpscale.loader import j
from tests.base_tests import BaseTests


@pytest.mark.integration
class Sendgrid(BaseTests):
    SMTP_SERVER = "imap.gmail.com"

    def setUp(self):
        self.sendgird_client_name = self.random_name()
        self.sendgrid_client = j.clients.sendgrid.get(name=self.sendgird_client_name)
        self.send_gird_api_key_token = os.getenv("SEND_GRID_API_KEY_TOKEN")
        self.recipient_mail = os.getenv("RECIPIENT_MAIL")
        self.recipient_pass = os.getenv("RECIPIENT_PASS")
        if self.send_gird_api_key_token and self.recipient_mail and self.recipient_pass:
            self.sendgrid_client.apikey = self.send_gird_api_key_token
            self.recipient_mail = self.recipient_mail
        else:
            raise Exception(
                "Please add (SEND_GRID_API_KEY_TOKEN, RECIPIENT_MAIL, RECIPIENT_PASS) as environment variables "
            )

        self.sender_mail = j.data.fake.email()
        self.subject = j.data.fake.sentence()
        self.attachment_type = "application/txt"
        file_name = self.random_name()
        self.attachment_path = f"/tmp/{file_name}.txt"
        # Writing txt to be used in attachemt
        j.sals.fs.write_file(path=self.attachment_path, data="i am testing")

    def test01_test_sendgrid_send_mail(self):
        """Test for sending an email without attachment.

        **Test Scenario**

        - Get sendgrid object.
        - Send the email.
        - Validate that the email send by accessing the receiver mail and check the inbox for the send email.
        - Delete the send email from the receiver mail inbox.
        """
        self.sendgrid_client.send(sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail])
        self.assertTrue(self.await_validate_mail(validate_attachment=False))

    def test02_test_sendgrid_send_mail_with_attachment(self):
        """Test for sending an email without attachment.

        **Test Scenario**

        - Get sendgrid object.
        - Create attachment.
        - Add the attachment to sendgrid object.
        - Send the email.
        - Validate that the email send by accessing the receiver mail and check the inbox for the send email.
        - Delete the send email from the receiver mail inbox.
        """
        attach = self.sendgrid_client.build_attachment(filepath=self.attachment_path, typ=self.attachment_type)
        self.sendgrid_client.send(
            sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail], attachments=[attach]
        )
        self.assertTrue(self.await_validate_mail(validate_attachment=False, attachment_type=self.attachment_type))

    def read_email_from_gmail(self, validate_attachment=True, attachment_type=None):
        try:
            mail = imaplib.IMAP4_SSL(self.SMTP_SERVER)
            mail.login(self.recipient_mail, self.recipient_pass)
            mail.select("inbox")
            _, data = mail.search(None, "ALL")
            mail_ids = data[0]
            id_list = mail_ids.split()
            first_email_id = int(id_list[0])
            latest_email_id = int(id_list[-1])
            for i in range(latest_email_id, first_email_id, -1):
                if self.validate_mail(mail, i, validate_attachment, attachment_type):
                    # Delete the mail
                    mail.store(str(i).encode(), "+FLAGS", "\\Deleted")
                    mail.expunge()
                    return True
            return False
        except Exception as e:
            print(str(e))

    def validate_mail(self, mail, mail_index, validate_attachment=True, attachment_type=None):
        _, data = mail.fetch(str(mail_index), "(RFC822)")
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg["subject"]
                email_from = msg["from"]
                if email_from == self.sender_mail:
                    self.assertEqual(email_subject, self.subject)
                    if validate_attachment:
                        attachment = msg.get_payload()[1]
                        self.assertEqual(attachment.get_content_type(), attachment_type)
                    return True
        return False

    def await_validate_mail(self, seconds=10, validate_attachment=True, attachment_type=None):
        for _ in range(seconds):
            if self.read_email_from_gmail(validate_attachment, attachment_type):
                return True
            gevent.sleep(1)
        return False

    def tearDown(self):
        j.clients.sendgrid.delete(self.sendgird_client_name)
        os.remove(self.attachment_path)
