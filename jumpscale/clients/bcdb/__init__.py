from jumpscale.core.base import StoredFactory
from .client import Client, HTTPClient


# class BCDBFactory(StoredFactory):
#     def new(self, name, *args, **kwargs):
#         if kwargs.get("admin"):
#             self.type = ZDBAdminClient
#         return super().new(name, *args, **kwargs)


def export_module_as():

    return StoredFactory(HTTPClient)
