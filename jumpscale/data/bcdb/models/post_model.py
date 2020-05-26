from .base import ModelBase

class QuoteModel(ModelBase):
    _schema = """
    @url = quote
    author** = "Anonymous" (S)
    quote*** = "" (S)
    """
    _name = "quote"