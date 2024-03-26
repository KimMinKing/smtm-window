import time
from collections import defaultdict

class TTLDictionary:
    def __init__(self, ttl):
        self.dictionary = defaultdict(dict) 
        self.ttl_start_time = None
        self.ttl_duration = ttl

    def start_ttl(self):
        self.ttl_start_time = time.time()
        

    def is_expired(self):
        return time.time() >= self.ttl_start_time + self.ttl_duration

    def reset(self, callback=None, market=None):
        if callback is not None:
            self.callback=callback
            print("콜백했어")
            self.callback(self.dictionary, market)
        self.dictionary = defaultdict(dict)
        self.ttl_start_time = None

    def add_value(self, key, value, value2):
        if self.ttl_start_time is None:
            print("Error: TTL not started. Use start_ttl method to start TTL.")
            return
        self.dictionary[key][value]={value2:0}
        #[KRW-BTC][161000]={BID:0}

    def __str__(self):
        return str(self.dictionary)
