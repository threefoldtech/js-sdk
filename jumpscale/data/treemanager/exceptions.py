from jumpscale.core.exceptions import JSException


class NameExistsError(JSException):
    pass


class EmptyNameError(JSException):
    pass


class RootRemoveError(JSException):
    pass
