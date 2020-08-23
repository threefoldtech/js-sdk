import requests
from jumpscale.data import time as jstime

BASE_URL = "https://crt.sh/?q={}&output=json"
RATE_LIMIT = 50


def fetch_domain_certs(domain):
    """return all certificates issued to a specific domain

    Args:
        domain (str): parent domain

    Returns:
        list: of dicts of the certs. keys (issuer_ca_id, issuer_name, name_value, id, entry_timestamp, not_before, not_after)

    Raises:
        requests.exceptions.HTTPError
    """
    url = BASE_URL.format(domain)
    result = requests.get(url)
    if result.status_code != 200:
        result.raise_for_status()
    return result.json()


def has_reached_limit(domain):
    """check if a domain has reached the rate limit for issues certs

    Args:
        domain (str): parent domain

    Returns:
        bool: True if the limit has been reached

    Raises:
        requests.exceptions.HTTPError
    """
    all_certs = fetch_domain_certs(domain)
    count = 0
    now = jstime.utcnow()
    start_date = now.shift(days=-7)
    for cert in all_certs:
        # we will check using date only. entry_timestamp example "2020-08-23T12:15:27.833"
        t = jstime.Arrow.strptime(cert["entry_timestamp"].split("T")[0], "%Y-%m-%d").to("utc")
        if t >= start_date:
            count += 1
    return count >= RATE_LIMIT


def has_certificate(domain):
    """check if the specified domain name has an issued cert

    Args:
        domain (str): parent domain

    Returns:
        dict: cert dict if a cert was issued. else None

    Raises:
        requests.exceptions.HTTPError
    """
    all_certs = fetch_domain_certs(domain)
    for cert in all_certs:
        if cert["name_value"] == domain:
            return cert
