_NULL_INT = 2147483647


def _next_workload_id(reservation):
    """
    returns the next workload id available in the reservation
    """
    max_work_load = 0
    for _type in [
        "zdbs",
        "volumes",
        "containers",
        "networks",
        "kubernetes",
        "proxies",
        "reverse_proxies",
        "subdomains",
        "domain_delegates",
    ]:
        for workload in getattr(reservation.data_reservation, _type):
            if workload.workload_id < _NULL_INT and max_work_load < workload.workload_id:
                max_work_load = workload.workload_id
    return max_work_load + 1
