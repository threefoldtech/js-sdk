from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.god import j
from trello import TrelloClient as TrelloAPIClient
from trello.util import create_oauth_token


class TrelloClient(Client):

    name = fields.String()
    api_key_ = fields.String()
    secret = fields.String()
    access_token = fields.String()
    acess_token_secret= fields.String()

    def __init__(self):
        super().__init__()
        self.__client = None
    
    @property
    def trello_client(self):

        if not self.token_secret:
            # print("**WILL TRY TO DO OAUTH SESSION")
            access_token = create_oauth_token(key=self.api_key, secret=self.secret)
            self.access_token_ = access_token["oauth_token"]
            self.access_token_secret = access_token["oauth_token_secret"]

        self.client = TrelloAPIClient(api_key=self.api_key_, api_secret=self.secret, token=self.token, token_secret=self.token_secret)

