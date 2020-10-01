import os
import string
import gevent
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
        if os.getenv("SEND_GRID_API_KEY_TOKEN") and os.getenv("RECIPIENT_MAIL"):
            self.test.apikey = os.getenv("SEND_GRID_API_KEY_TOKEN")
            self.recipient_mail = os.getenv("RECIPIENT_MAIL")
        else:
            raise Exception("Please add (SEND_GRID_API_KEY_TOKEN, RECIPIENT_MAIL) as environment variables ")

        self.sender_mail = j.data.fake.email()
        self.subject = j.data.fake.sentence()
        self.attachment_type = "application/txt"
        file_name = generate_rand_text(10, string.ascii_letters)
        self.attachment_path = f"/tmp/{file_name}.txt"
        # Writing pdf to be used in attachemt
        j.sals.fs.write_file(path=self.attachment_path, data="i am testing")

    def test01_test_sendgrid_send_mail(self):
        """Test for sending an email without attachment
        **.Test Scenario**
        #. Get sendgrid object
        #. Send the email
        #. Validate that the email send by accessing the receiver mail and check the inbox for the send email.
        #. Delete the send email from the receiver mail inbox.
        """
        res = self.test.send(sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail])
        self.assertIsNone(res)
        self.assertTrue(self.await_validate_mail(validate_attachment=False))

    def test02_test_sendgrid_send_mail_with_attachment(self):
        """Test for sending an email without attachment
        **.Test Scenario**
        #. Get sendgrid object
        #. Create attachment
        #. Add the attachment to sendgrid object
        #. Send the email
        #. Validate that the email send by accessing the receiver mail and check the inbox for the send email.
        #. Delete the send email from the receiver mail inbox.
        """
        attach = self.test.build_attachment(filepath=self.attachment_path, typ=self.attachment_type)
        res = self.test.send(
            sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail], attachments=[attach]
        )
        self.assertIsNone(res)
        self.assertTrue(self.await_validate_mail(validate_attachment=False, attachment_type=self.attachment_type))

    def read_email_from_gmail(self, validate_attachment=True, attachment_type=None):
        try:
            if os.getenv("SMTP_SERVER") and os.getenv("RECIPIENT_MAIL") and os.getenv("RECIPIENT_PASS"):
                mail = imaplib.IMAP4_SSL(os.getenv("SMTP_SERVER"))
                mail.login(os.getenv("RECIPIENT_MAIL"), os.getenv("RECIPIENT_PASS"))
            else:
                raise Exception("Please add (SMTP_SERVER, RECIPIENT_MAIL, RECIPIENT_PASS)  as environment variables ")
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
