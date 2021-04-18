"""
External API related helpers
"""
from bottle import abort, request, response, parse_auth
from jumpscale.loader import j

from .exceptions import BaseError, InvalidCredentials, MissingAuthorizationHeader, VDCNotFound
from ..vdc_helpers import threebot_vdc_helper


def format_error(error):
    """"
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
                # Get vdc instance and password
                vdc = get_vdc()
                if not vdc:
                    raise VDCNotFound(
                        500, "No VDCs where found, Please make sure to have it configured properly",
                    )

                # Get vdc and password password from request Authorization header with Basic type
                auth_header = request.headers.get("Authorization")
                if not auth_header:
                    raise MissingAuthorizationHeader(403, "Authorization header is not set")

                vdc_name, password = parse_auth(auth_header)
                if not vdc.validate_password(password) or vdc_name != vdc.vdc_name:
                    raise InvalidCredentials(403, "Invalid credentials")

                result = function(vdc, *args, **kwargs)
                if serialize:
                    response.content_type = "application/json"
                    return j.data.serializers.json.dumps(result)

                return result
            except BaseError as error:
                function_name = function.__name__
                # TODO: logging plugin for bottle to log requests using j.logger
                j.logger.error(f"Error while calling {function_name}: {error}")
                return format_error(error)

        return wrapper

    return decorator
