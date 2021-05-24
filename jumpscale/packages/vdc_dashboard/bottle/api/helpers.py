"""
External API related helpers
"""
from functools import wraps

from bottle import parse_auth, request, response
from jumpscale.loader import j

from ..models import APIKeyFactory
from ..vdc_helpers import threebot_vdc_helper
from .exceptions import (
    BaseError,
    InvalidCredentials,
    MissingAuthorizationHeader,
    UnknownError,
    VDCNotFound,
)


def logger(function):
    """
    Wrap a Bottle request so that a log line is emitted after it's handled in case of errors to make it easy to debug.
    """

    @wraps(function)
    def _logger(*args, **kwargs):
        actual_response = function(*args, **kwargs)

        # get function name
        closures = function.__closure__
        if closures:
            api_function_name = closures[0].cell_contents.__name__
        else:
            api_function_name = function.__name__

        if 200 <= response.status_code < 300:
            j.logger.info(f"{api_function_name}: {request.method} {response.status}: {request.url} ")
        else:
            resp = j.data.serializers.json.loads(actual_response)
            j.logger.error(
                f"{request.method} {request.path}: Error {resp.get('status')}, {resp.get('type')}: {resp.get('message')}, "
                f"Function {api_function_name} , "
                f"request params: {dict(request.params)}, "
                f"request body: {request.body.read().decode()}"
            )
        return actual_response

    return _logger


def format_error(error):
    """n
    formats an error as json

    Args:
        error (BaseError): error object

    Returns
        str: json formatted error with status, type and message fields
    """
    if isinstance(error, BaseError):
        status = error.status
    else:
        status = 400

    error_type = error.__class__.__name__
    try:
        message = error.message
    except AttributeError:
        message = str(error)

    data = {"status": status, "type": error_type, "message": message}
    response.status = status
    response.content_type = "application/json"
    return j.data.serializers.json.dumps(data)


def get_vdc(load_info=True):
    vdcs = j.sals.vdc.list_all()
    if vdcs:
        vdc_full_name = list(vdcs)[0]
        return j.sals.vdc.find(vdc_full_name, load_info=load_info)


def get_full_vdc_info(vdc):
    return threebot_vdc_helper(vdc=vdc)


def vdc_route(serialize=True):
    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                function_name = function.__name__

                # Get vdc instance and password
                vdc = get_vdc()
                if not vdc:
                    raise VDCNotFound(
                        500, "No VDCs where found, Please make sure to have it configured properly",
                    )

                # Get vdc name and password from request Authorization header with Basic type
                auth_header = request.headers.get("Authorization")
                if not auth_header:
                    raise MissingAuthorizationHeader(403, "Authorization header is not set")

                name, password = parse_auth(auth_header)
                authorized = False
                if vdc.validate_password(password) and name == vdc.vdc_name:
                    authorized = True
                elif name in APIKeyFactory.list_all():
                    api_key = APIKeyFactory.find(name)
                    if password == api_key.key:
                        authorized = True

                if not authorized:
                    raise InvalidCredentials(403, "Invalid credentials")

                result = function(vdc, *args, **kwargs)
                if serialize:
                    response.content_type = "application/json"
                    return j.data.serializers.json.dumps(result)

                return result
            except BaseError as error:
                return format_error(error)
            except Exception as error:
                j.logger.exception(f"Unhandled exception when calling {function_name}: {error}", exception=error)
                return format_error(UnknownError(500, "Unknown error, please contact support"))

        return wrapper

    return decorator
