def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .trello import TrelloClient

    return StoredFactory(TrelloClient)
