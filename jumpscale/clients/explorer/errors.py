from requests import HTTPError


def _get_reason(resp):
    if "application/json" == resp.headers.get("Content-Type"):
        reason = resp.json()["error"]
    else:
        reason = resp.text
    return reason


def raise_for_status(resp, *args, **kwargs):
    http_error_msg = ""
    if 400 <= resp.status_code < 500:
        reason = _get_reason(resp)
        http_error_msg = f"{resp.status_code} Client Error: {reason} for url: {resp.url}"

    elif 500 <= resp.status_code < 600:
        reason = _get_reason(resp)
        http_error_msg = f"{resp.status_code} Server Error: {reason} for url: {resp.url}"

    if http_error_msg:
        raise HTTPError(http_error_msg, response=resp)
