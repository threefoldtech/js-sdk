from jumpscale.core import exceptions


class BaseError(exceptions.Base):
    """a generic base error for bcdb rest, with status code"""

    def __init__(self, status, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.status = status


class VDCNotFound(BaseError):
    pass


class MissingAuthorizationHeader(BaseError):
    pass


class InvalidCredentials(BaseError):
    pass


class MissingArgument(BaseError):
    pass


class StellarServiceDown(BaseError):
    pass


class FlavorNotSupported(BaseError):
    pass


class NoEnoughCapacity(BaseError):
    pass


class AdddingNodeFailed(BaseError):
    pass


class CannotDeleteMasterNode(BaseError):
    pass


class ZDBDeploymentFailed(BaseError):
    pass


class ZDBDeletionFailed(BaseError):
    pass


class KubeConfigNotFound(BaseError):
    pass


class InvalidKubeConfig(BaseError):
    pass


class ZStorConfigNotFound(BaseError):
    pass


class InvalidZStorConfig(BaseError):
    pass


class NoEnoughFunds(BaseError):
    pass


class BadRequestError(BaseError):
    pass


class UnknownError(BaseError):
    pass
