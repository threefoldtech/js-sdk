class BaseResource:
    def __init__(self, client):
        self._client = client
        self._session = client._session

    @property
    def _url(self):
        return self._client.url + f"/{self._resource}"
