"""Background poller for Rivian bridge HTTP API on TCM."""

import json
import threading
import time
import urllib.request


class RivianBridge:
    def __init__(self, url="http://172.28.1.64:8082"):
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
