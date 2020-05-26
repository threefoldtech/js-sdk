from .base import ModelBase

class DBModel(ModelBase):
    _schema = """
    @url = db
    host = "" (S)
    user = (O)!user
    """
    _name = "db"