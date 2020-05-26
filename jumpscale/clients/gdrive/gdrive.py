from google.oauth2 import service_account
from googleapiclient.discovery import build
from jumpscale.clients.base import Client
from jumpscale.core.base import fields


"""
JS-NG> cl = j.clients.gdrive.new("name")
JS-NG> cl.credfile = "/Downloads/pelagic-core-251306-8b2323198535.json"
JS-NG> cl.get_file('1kUHHSjtPNUN2dAJQSAeCWMvrZzUO2YNW')
{'kind': 'drive#file', 'id': '1kUHHSjtPNUN2dAJQSAeCWMvrZzUO2YNW', 'name': 'my.txt', 'mimeType': 'text/plain'}

cl.files.get_media(fileId='1kUHHSjtPNUN2dAJQSAeCWMvrZzUO2YNW')

JS-NG> cl.get_service('drive', 'v3')
<googleapiclient.discovery.Resource object at 0x7f3fa8982240>
"""


SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.appdata",
    "https://www.googleapis.com/auth/drive.scripts",
    "https://www.googleapis.com/auth/drive.metadata",
]

DRIVE_BUILD_VERSION = "v3"


class GdriveClient(Client):
    credfile = fields.String()

    def __init__(self):
        self.__credentials = None
        self.__files = None
        super().__init__()

    @property
    def credentials(self):
        if not self.__credentials:
            self.__credentials = service_account.Credentials.from_service_account_file(
                self.credfile, scopes=SCOPES
            )
        return self.__credentials

    @property
    def files(self):
        if not self.__files:
            drive = self.get_service("drive", DRIVE_BUILD_VERSION)
            self.__files = drive.files()
        return self.__files

    def get_service(self, name, version):
        return build(name, version, credentials=self.credentials)

    def get_file(self, file_id):
        return self.files.get(fileId=file_id).execute()

    def export_pdf(self, file_id, export_path):
        response = self.files.export_media(fileId=file_id, mimeType="application/pdf").execute()
        with open(export_path, "wb") as expr:
            expr.write(response)
