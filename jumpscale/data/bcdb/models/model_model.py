from jumpscale.god import j

from .base import ModelBase, JSObjBase

class ModelModel(ModelBase):
    _schema = """
    @url = model
    name* = "" (S)
    model_class = "" (S)
    """
    _name = "model"    