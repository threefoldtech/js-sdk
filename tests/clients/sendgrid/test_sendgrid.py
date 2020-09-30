import os
import string
from unittest import TestCase
from jumpscale.loader import j


class Sendgrid(TestCase):
    def setUp(self):
        self.sendgird_client_name = j.data.idgenerator.nfromchoices(10, string.ascii_letters)
        self.test = j.clients.sendgrid.get(name=self.sendgird_client_name)
        self.test.apikey = os.environ.get("SEND_GRID_API_KEY_TOKEN")
        self.sender_mail = j.data.fake.email()
        self.recipient_mail = j.data.fake.email()
        self.subject = j.data.fake.sentence()
        file_name = j.data.idgenerator.nfromchoices(10, string.ascii_letters)
        self.attachment_path = f"/tmp/{file_name}.pdf"
        # Writing pdf to be used in attachemt
        j.sals.fs.write_file(path=self.attachment_path, data="i am testing")

    def test01_test_sendgrid_send_mail(self):
        res = self.test.send(sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail])
        self.assertIsNone(res)

    def test02_test_sendgrid_send_mail_with_attachment(self):
        attach = self.test.build_attachment(filepath=self.attachment_path)
        res = self.test.send(
            sender=self.sender_mail, subject=self.subject, recipients=[self.recipient_mail], attachments=[attach]
        )
        self.assertIsNone(res)

    def tearDown(self):
        j.clients.sendgrid.delete(self.sendgird_client_name)
        os.remove(self.attachment_path)
