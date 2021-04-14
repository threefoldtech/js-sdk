from bottle import abort, request
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

            # FIXME we should get md5 password from Authorization header with Digest type
            # Get password from request
            data = j.data.serializers.json.loads(request.body.read())
            request_input_password = data.get("password")
            if not vdc.validate_password(request_input_password):
                return abort(403, "Wrong password is passed")
            return function(*args, **kwargs)

        return wrapper

    return decorator
