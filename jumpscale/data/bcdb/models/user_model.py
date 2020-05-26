from .base import ModelBase

class UserModel(ModelBase):
    _schema = """
    @url = user
    username = "" (S)
    password = "" (S)
    """
    _name = "user"