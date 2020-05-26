from .base import ModelBase

class TestModel(ModelBase):
    _schema = """
    @url = test
    a = 1 (I)
    """
    _name = "test"