from .base import ModelBase

class ProjModel(ModelBase):
    _schema = """
    @url = proj
    author* = "" (S)
    employees = 0 (I)
    company = "" (S)
    """
    _name = "proj"