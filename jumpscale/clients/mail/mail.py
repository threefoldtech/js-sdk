from jumpscale.loader import j
import smtplib
import mimetypes
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jumpscale.clients.base import Client
from jumpscale.core.base import fields


class MailClient(Client):
    name = fields.String()
    smtp_server = fields.String()
    smtp_port = fields.Integer()
    login = fields.String()
    password = fields.String()
    sender_email = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def is_ssl(self):
        return self.smtp_port in [465, 587]

    def send(self, recipients, sender="", subject="", message="", files=None, mimetype=None):
        """ Send an email to the recipients from the sender containing the message required and any attached files given by the paths in files
        :param recipients: Recipients of the message
        :type recipients: mixed, str or list
        :param sender: Sender of the email
        :type sender: str
        :param subject: Subject of the email
        :type subject: str
        :param message: Body of the email
        :type message: str
        :param files: List of paths to files to attach
        :type files: list of strings
        :param mimetype: Type of the body plain, html or None for autodetection
        :type mimetype: str
        """
        if not sender:
            sender = self.sender_email
        if isinstance(recipients, str):
            recipients = [recipients]
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.ehlo()
        if self.is_ssl:
            server.starttls()
        if self.login:
            server.login(self.login, self.password)

        if mimetype is None:
            if "<html>" in message:
                mimetype = "html"
            else:
                mimetype = "plain"

        msg = MIMEText(message, mimetype)

        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ",".join(recipients)

        if files:
            txtmsg = msg
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = ",".join(recipients)
            msg.attach(txtmsg)
            for fl in files:
                # Guess the content type based on the file's extension.  Encoding
                # will be ignored, although we should check for simple things like
                # gzip'd or compressed files.
                filename = j.sals.fs.basename(fl)
                ctype, encoding = mimetypes.guess_type(fl)
                content = j.sals.fs.read_file(fl)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                if maintype == "text":
                    attachement = MIMEText(content, _subtype=subtype)
                elif maintype == "image":
                    attachement = MIMEImage(content, _subtype=subtype)
                elif maintype == "audio":
                    attachement = MIMEAudio(content, _subtype=subtype)
                else:
                    attachement = MIMEBase(maintype, subtype)
                    attachement.set_payload(content)
                    # Encode the payload using Base64
                    encoders.encode_base64(attachement)
                # Set the filename parameter
                attachement.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(attachement)
        server.sendmail(sender, recipients, msg.as_string())
        server.close()
