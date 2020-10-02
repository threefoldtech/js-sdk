from urllib.parse import urlparse
import requests
import json
import redis
import sys

class ContainerStatsMonitor:
    def __init__(self):
        self.host = None
        self.port = None
        self.channel = None

        self.redis = None
        self.pubsub = None
        self.previous = None

    def endpoint(self, endpoint):
        params = urlparse(endpoint)

        self.host = params.netloc.split(':')[0]
        self.port = params.netloc.split(':')[1]
        self.channel = params.path[1:]

        return self.connect()

    #
    # Reservation Parser
    #
    def reservation(self, url):
        reservation = requests.get(url).json()

        if len(reservation['stats']) == 0:
            raise RuntimeError("No statistics endpoint defined")

        if reservation['stats'][0]['type'] != "redis":
            raise RuntimeError("Invalid statistics type, not supported")

        return self.endpoint(reservation['stats'][0]['data']['endpoint'])

    def connect(self):
        print("[+] connecting: [%s:%s / %s]" % (self.host, self.port, self.channel))

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
        # initial message
        if self.previous == None:
            self.previous = stats
            return

        usage = stats['cpu_usage'] - self.previous['cpu_usage']
        difftime = stats['timestamp'] - self.previous['timestamp']
        computed = usage / (difftime * 10000000)

        self.previous = stats

        print("CPU Usage: %0.2f%% / RAM: %.2f MB" % (computed, stats['memory_usage'] / 1000000))

        pass

    #
    # Monitoring
    #
    def monitor_once(self):
        data = self.pubsub.get_message(timeout=1)
        if data == None:
            return

        if data['type'] != 'message':
            return

        info = data['data'].decode('utf-8')
        stats = json.loads(info)

        self.dump(stats)

    def monitor(self):
        print("[+] waiting for statistics")

        while True:
            self.monitor_once()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise RuntimeError("Missing reservation url argument")

    # url = "https://explorer.maxux.net/api/v1/reservations/workloads/103"
    url = sys.argv[1]

    s = ContainerStats(url)
    s.monitor()
