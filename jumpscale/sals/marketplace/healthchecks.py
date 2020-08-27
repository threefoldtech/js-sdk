from bottle import route, run


@route("/api/health")
def index():
    """Returns the flist health information

    Returns:
        [type]: [description]
    """
    # TODO: Define each status according to the flist needs, this is dummy object
    detailed_status = {"redis": "OK", "postgres": "OK", "bottle": "OK", "backup_service": "ERROR"}

    return {"status": "OK", "detailed": detailed_status}


run(host="0.0.0.0", port=8881)
