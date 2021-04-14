from bottle import abort, request, parse_auth
from jumpscale.loader import j


def controller_authorized():
    def decorator(function):
        def wrapper(*args, **kwargs):
            # Get vdc instance and password
            if not j.sals.vdc.list_all():
                abort(
                    500, "Couldn't find any vdcs on this machine, Please make sure to have it configured properly",
                )
            vdc_full_name = list(j.sals.vdc.list_all())[0]
            vdc = j.sals.vdc.get(vdc_full_name)

            # Get password from request Authorization header with Basic type
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return abort(403, "Password not passed in the Authorization header")
            _, request_input_password = parse_auth(auth_header)
            if not vdc.validate_password(request_input_password):
                return abort(403, "Wrong password is passed")
            return function(*args, **kwargs)

        return wrapper

    return decorator
