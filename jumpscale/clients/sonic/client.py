from sonic import SearchClient, IngestClient
from jumpscale.clients.base import Client
from jumpscale.core.base import Base, fields


class SonicClient(Client):
    host = fields.String(default="127.0.0.1")
    port = fields.Integer(default=1491)
    password = fields.String(default="password")

    def __init__(self):
        super().__init__()

        self.cached_client_search = None
        self.cached_client_ingest = None

        self.push = self.client_ingest.push
        self.pop = self.client_ingest.pop
        self.count = self.client_ingest.count
        self.flush = self.client_ingest.flush
        self.flush_collection = self.client_ingest.flush_collection
        self.flush_bucket = self.client_ingest.flush_bucket
        self.flush_object = self.client_ingest.flush_object

        self.query = self.client_search.query
        self.suggest = self.client_search.suggest

    @property
    def client_ingest(self):
        if not self.cached_client_ingest:
            self.cached_client_ingest = IngestClient(host=self.host, port=self.port, password=self.password)
        return self.cached_client_ingest

    @property
    def client_search(self):
        if not self.cached_client_search:
            self.cached_client_search = SearchClient(host=self.host, port=self.port, password=self.password)
        return self.cached_client_search
