"""This module is providing some helper to monitor stuff running on zos

# ContainerStatsMonitor

This class is made for quickly monitor container statistics. Current zos
implementation support streaming statistics to a redis channel continuously.
This helper extract theses information and present them to the user correctly.

```
> s = j.tools.zos.monitor.ContainerStatsMonitor()
> s.endpoint("redis://10.241.0.232:6379/statsx")
> s.monitor()
2020-10-14 14:47:24.539 | INFO     | jumpscale.tools.zos.monitor:dump:68 - CPU Usage: 0.00% / RAM: 4.01 MB
...
```
"""

from jumpscale.loader import j
from urllib.parse import urlparse
import requests
import json
import redis
import sys


class ContainerStatsMonitor:
    def __init__(self):
        """Initialize the class with defaults values"""
        self.host = None
        self.port = None
        self.channel = None

        self.redis = None
        self.pubsub = None
        self.previous = None

    def endpoint(self, endpoint):
        """Parse an endpoint provided to zos redis container stats
        and prepare the class to use theses data

        Returns:
            bool: result of connect() chained
        """
        params = urlparse(endpoint)

        self.host = params.netloc.split(":")[0]
        self.port = params.netloc.split(":")[1]
        self.channel = params.path[1:]

        return self.connect()

    #
    # Reservation Parser
    #
    def reservation(self, url):
        resp = requests.get(url)
        resp.raise_for_status()
        reservation = resp.json()

        if not reservation["stats"]:
            raise RuntimeError("No statistics endpoint defined")

        if reservation["stats"][0]["type"] != "redis":
            raise RuntimeError("Invalid statistics type, not supported")

        return self.endpoint(reservation["stats"][0]["data"]["endpoint"])

    def connect(self):
        """Connect to the redis endpoint set previously

        Returns:
            bool: True if connected, Exception on error
        """
        j.logger.debug(f"connecting [{self.host}:{self.port} / {self.channel}]")

        self.redis = redis.Redis(self.host, self.port)
        if not self.redis.ping():
            raise RuntimeError("Could not connect redis")

        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel)

        return True

    #
    # Statistics Dump
    #
    def dump(self, stats):
        """Print available metrics and update previous value with current one"""
        # initial message
        if not self.previous:
            self.previous = stats
            return

        usage = stats["cpu_usage"] - self.previous["cpu_usage"]
        difftime = stats["timestamp"] - self.previous["timestamp"]
        computed = usage / (difftime * 10000000)
        memory = stats["memory_usage"] / 1000000

        self.previous = stats

        j.logger.info(f"CPU Usage: {computed:.2f}% / RAM: {memory:.2f} MB")

    #
    # Monitoring
    #
    def monitor_once(self):
        """Wait and parse a single line of statistics"""
        data = self.pubsub.get_message(timeout=1)
        if not data:
            return

        if data["type"] != "message":
            return

        info = data["data"].decode("utf-8")
        stats = json.loads(info)

        self.dump(stats)

    def monitor(self):
        """Wait and parse continuously statistics available"""
        j.logger.debug("waiting for statistics")

        while True:
            self.monitor_once()
