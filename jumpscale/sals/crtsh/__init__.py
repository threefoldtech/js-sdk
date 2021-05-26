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


def count_domain_certs_since(domain, days=7):
    """check if a domain has reached the rate limit for issues certs

    Args:
        domain (str): parent domain
        days (int): number of days to be checked since

    Returns:
        int: number of certs issued by letsencrypt

    Raises:
        requests.exceptions.HTTPError
    """
    all_certs = fetch_domain_certs(domain)
    count = 0
    now = jstime.utcnow()
    domains = set()
    start_date = now.shift(days=-1 * days)
    for cert in all_certs:
        # rate limit is 50 certs every week. so we check how many certs were issued within the last 7 days
        # we will check using date only. entry_timestamp example "2020-08-23T12:15:27.833"
        # check only for letsencrypt
        if "Let's Encrypt" not in cert["issuer_name"]:
            continue
        t = jstime.Arrow.strptime(cert["entry_timestamp"].split("T")[0], "%Y-%m-%d").to("utc")
        subdomain = cert["name_value"].split(".")[0]
        if t >= start_date:
            domains.add(subdomain)
    count = len(domains)
    return count


def has_reached_limit(domain, limit=RATE_LIMIT):
    """check if a domain has reached the rate limit for issues certs

    Args:
        domain (str): parent domain
        limit (int): limit to be checked against. defaults to 50

    Returns:
        bool: True if the limit has been reached

    Raises:
        requests.exceptions.HTTPError
    """
    count = count_domain_certs_since(domain)
    return count >= limit


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
