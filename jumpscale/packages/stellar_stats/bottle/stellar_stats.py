import datetime

from beaker.middleware import SessionMiddleware
from bottle import Bottle, request

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS

from jumpscale.packages.stellar_stats.bottle.stats_service import StatisticsCollector

app = Bottle()


@app.route("/api/stats")
def get_stats():
    """Statistics about TFT, TFTA and FreeTFT

    Args:
        network (str ["test", "public"], optional): Defaults to "public".
        tokencode (str ["TFT", "TFTA", "FreeTFT"], optional): Defaults to "TFT".
        detailed (bool, optional): Defaults to False.
    """
    query_params = request.query.decode()
    network = query_params.get("network", "public")
    tokencode = query_params.get("tokencode", "TFT")
    detailed = j.data.serializers.json.loads(query_params.get("detailed", "false"))
    res = {}

    # cache the request in local redis
    redis = j.clients.redis.get("redis_instance")
    cached_data = redis.get(f"{network}-{tokencode}-{detailed}")
    if cached_data:
        return cached_data

    collector = StatisticsCollector(network)
    stats = collector.getstatistics(tokencode, detailed)
    res["total_tokens"] = f"{stats['total']:,.7f}"
    res["total_accounts"] = f"{stats['num_accounts']}"
    res["total_locked_tokens"] = f"{stats['total_locked']:,.7f}"
    if detailed:
        res["locked_tokens_info"] = []
        for locked_amount in stats["locked"]:
            res["locked_tokens_info"].append(
                f"{locked_amount['amount']:,.7f} locked until {datetime.datetime.fromtimestamp(locked_amount['until'])}"
            )
    results = j.data.serializers.json.dumps(res)
    redis.set(f"{network}-{tokencode}-{detailed}", results, ex=600)

    return results


app = SessionMiddleware(app, SESSION_OPTS)
