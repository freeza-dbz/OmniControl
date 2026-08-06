import base64
import os
from datetime import datetime

class ScreenshotService:
    @staticmethod
    def save_screenshot(encoded_content):
        os.makedirs("screenshot", exist_ok=True)
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
        path = os.path.join("screenshot", filename)
        with open(path, "wb") as f:
            f.write(base64.b64decode(encoded_content))
        return path

    @staticmethod
    def request_screenshot(sio, target):
        sio.emit("screenshot", {"target": target})
