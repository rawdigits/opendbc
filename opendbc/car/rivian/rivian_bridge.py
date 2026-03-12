"""Background poller for Rivian bridge HTTP API on TCM."""

import json
import os
import threading
import time
import urllib.request

REPO_CONF = "/data/openpilot/rivian-bridge.conf"
DATA_CONF = "/data/rivian-bridge.conf"
DEFAULT_URL = "http://172.28.1.64:8082"


def _read_bridge_url():
    for path in (REPO_CONF, DATA_CONF):
        try:
            with open(path) as f:
                url = f.read().strip()
                if url:
                    return url
        except FileNotFoundError:
            continue
    return DEFAULT_URL


class RivianBridge:
    def __init__(self, url=None):
        if url is None:
            url = _read_bridge_url()

        self.url = url
        self.state = {}
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self):
        while True:
            try:
                req = urllib.request.urlopen(f"{self.url}/state", timeout=1)
                data = json.loads(req.read())
                with self._lock:
                    self.state = data
            except Exception:
                pass
            time.sleep(0.3)  # Poll at ~3Hz

    @property
    def set_speed_ms(self):
        with self._lock:
            return self.state.get("set_speed_ms", 0)

    @property
    def follow_personality(self):
        with self._lock:
            return self.state.get("follow_personality", -1)

    @property
    def stale(self):
        with self._lock:
            return self.state.get("stale", True)
