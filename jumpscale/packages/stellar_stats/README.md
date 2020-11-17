# Stellar stats

## Install the package

```python3
JS-NG> server = j.servers.threebot.get("default")
JS-NG> server.packages.add(path="/root/js-sdk/jumpscale/packages/stellar_stats")
JS-NG> server.save()
JS-NG> server.start()
```

- On production add the domain in the `package.toml` currently is set to `statsdata.threefoldtoken.com`

## Endpoint

https://<host>/stellar_stats/api/stats
https://<host>/stellar_stats/api/total_tft
https://<host>/stellar_stats/api/total_unlocked_tft

## Query params

- network: (str ["test", "public"], optional): Defaults to "public".
- tokencode: (str ["TFT", "TFTA", "FreeTFT"], optional): Defaults to "TFT".
- detailed: (bool, optional): Defaults to False.


## Examples

- https://localhost/stellar_stats/api/stats
- https://localhost/stellar_stats/api/stats?network=public
- https://localhost/stellar_stats/api/stats?tokencode=TFTA
- https://localhost/stellar_stats/api/stats?network=public&tokencode=TFTA
- https://localhost/stellar_stats/api/stats?network=public&tokencode=TFTA&detailed=true
- https://localhost/stellar_stats/api/total_tft
- https://localhost/stellar_stats/api/total_unlocked_tft
