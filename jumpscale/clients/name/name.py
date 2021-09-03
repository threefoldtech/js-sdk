from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from namecom import Name
from jumpscale.core import events
from jumpscale.core.base.events import AttributeUpdateEvent


class NameClientAttributeUpdated(AttributeUpdateEvent):
    pass


class NameClient(Client):
    username = fields.String()
    token = fields.Secret()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None

    def _attr_updated(self, name, value):
        super()._attr_updated(name, value)
        # this will allow other people to listen to this event too
        event = NameClientAttributeUpdated(self, name, value)
        events.notify(event)

        # reset client
        self.__client = None

    @property
    def nameclient(self):
        if not self.__client:
            self.__client = Name(self.username, self.token)
        return self.__client
