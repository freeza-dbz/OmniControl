import time
import threading

class HeartbeatService:
    def __init__(self, sio, device_id, heartbeat_interval=5):
        self.sio = sio
        self.device_id = device_id
        self.heartbeat_interval = heartbeat_interval
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while self.sio.connected:
            time.sleep(self.heartbeat_interval)
            self.sio.emit("heartbeat", {"device_id": self.device_id})
