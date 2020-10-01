import os
import string
import pytest
import gevent
import time
import imaplib
import email
from unittest import TestCase
from jumpscale.loader import j


def generate_rand_text(char_count, choices):
    return j.data.idgenerator.nfromchoices(10, string.ascii_letters)


class Sendgrid(TestCase):
    def setUp(self):
        self.sendgird_client_name = generate_rand_text(10, string.ascii_letters)
        self.test = j.clients.sendgrid.get(name=self.sendgird_client_name)
        self.test.apikey = os.environ.get("SEND_GRID_API_KEY_TOKEN")
        self.sender_mail = j.data.fake.email()
        self.recipient_mail = os.environ.get("RECIPIENT_MAIL")
        self.subject = j.data.fake.sentence()
        self.attachment_type = "application/txt"
        file_name = generate_rand_text(10, string.ascii_letters)
        self.attachment_path = f"/tmp/{file_name}.txt"
        # Writing pdf to be used in attachemt
        j.sals.fs.write_file(path=self.attachment_path, data="i am testing")

    def test01_test_sendgrid_send_mail(self):
        res = self.test.send(sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail])
        self.assertIsNone(res)

    def test02_test_sendgrid_send_mail_with_attachment(self):
        attach = self.test.build_attachment(filepath=self.attachment_path, typ=self.attachment_type)
        res = self.test.send(
            sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail], attachments=[attach]
        )
        self.assertIsNone(res)
        gevent.sleep(10)
        self.assertTrue(self.read_email_from_gmail(self.sender_mail, self.subject, self.attachment_type))

    def read_email_from_gmail(self, sender_mail, subject, attachment_type):
        try:

            mail = imaplib.IMAP4_SSL(os.environ.get("SMTP_SERVER"))
            mail.login(os.environ.get("RECIPIENT_MAIL"), os.environ.get("RECIPIENT_PASS"))
            mail.select("inbox")

            _, data = mail.search(None, "ALL")
            mail_ids = data[0]

            id_list = mail_ids.split()
            first_email_id = int(id_list[0])
            latest_email_id = int(id_list[-1])

            for i in range(latest_email_id, first_email_id, -1):
                # need str(i)
                _, data = mail.fetch(str(i), "(RFC822)")

                for response_part in data:
                    if isinstance(response_part, tuple):
                        # from_bytes, not from_string
                        msg = email.message_from_bytes(response_part[1])
                        email_subject = msg["subject"]
                        email_from = msg["from"]
                        if email_from == sender_mail:
                            self.assertEqual(email_subject, subject)
                            attachment = msg.get_payload()[1]
                            self.assertEqual(attachment.get_content_type(), attachment_type)
                            return True
            return False
        except Exception as e:
            print(str(e))

    def tearDown(self):
        j.clients.sendgrid.delete(self.sendgird_client_name)
        os.remove(self.attachment_path)
