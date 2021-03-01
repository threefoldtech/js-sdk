"""This module is providing some helper to report stuff running on zos

- get_public_ip_usage example:

    ```python
    JS-NG> j.tools.zos.reporting.get_public_ip_usage()

    +========================= RESERVED IPS =========================+
    user: vdc_magidentfinal_test6       |	tid: 1751 |	wid: 7955
    user: dylanv.3bot                   |	tid: 48   |	wid: 7124
    user: vdc_hanafy_testvdc01          |	tid: 1737 |	wid: 7315
    user: vdc_ahmedthabet_demobackup    |	tid: 1763 |	wid: 8380
    +----------------------------------------------------------------+
    busy: 4     |	    free: 4         |	total:8
    +=========================     DONE     =========================+

    JS-NG> j.tools.zos.reporting.get_public_ip_usage("testnet")

    +========================= RESERVED IPS =========================+
    user: vdc_waleedhammam_thabet465    |	tid: 3214 |	wid: 515942
    user: vdc_ahmedthabet_demox1234     |	tid: 3219 |	wid: 516092
    user: vdc_magidentfinal_testoooo    |	tid: 3228 |	wid: 516807
    user: vdc_ayoubm_testayoub          |	tid: 3217 |	wid: 516013
    +----------------------------------------------------------------+
    busy: 4     |	    free: 26        |	total:30
    +=========================     DONE     =========================+

    ```

"""

from jumpscale.loader import j

PUBLIC_IP_FARMS = {"devnet": "lochristi_dev_lab", "testnet": "freefarm", "mainnet": "freefarm"}
DEFAULT_EXPLORER_URLS = {
    "mainnet": "https://explorer.grid.tf/api/v1",
    "testnet": "https://explorer.testnet.grid.tf/api/v1",
    "devnet": "https://explorer.devnet.grid.tf/api/v1",
}


def get_public_ip_usage(explorer_name: str = "devnet"):
    """Provide a list of the used/free public ips

    Args:
        explorer (str, optional): explorer name should be in ["devnet", "testnet", "mainnet"]. Defaults to "devnet".

    Returns:
        str: nice view for the used ips or json
    """
    print("\n+========================= RESERVED IPS =========================+")
    explorer = j.clients.explorer.get_by_url(DEFAULT_EXPLORER_URLS[explorer_name])
    c = 0
    if not explorer_name in ["devnet", "testnet", "mainnet"]:
        raise j.exceptions.Value(f"Explorers: devnet, testnet, mainnet are only supported, you passed {explorer_name}")
    farm = explorer.farms.get(farm_name=PUBLIC_IP_FARMS[explorer_name])
    for ip in farm.ipaddresses:
        if not ip.reservation_id:
            continue
        c += 1
        workload = explorer.workloads.get(ip.reservation_id)
        owner_tid = workload.info.customer_tid
        user = explorer.users.get(owner_tid)
        print(f"user: {user.name:30}|\ttid: {owner_tid:<5}|\twid: {workload.id}")
    print("+----------------------------------------------------------------+")
    print(
        f"busy: {c:<6}|\t    free: {len(farm.ipaddresses)-c:<10}|\ttotal:{len(farm.ipaddresses):<3}"
        "\n+=========================     DONE     =========================+\n"
    )
