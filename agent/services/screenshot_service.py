import io
import base64
import pyautogui

class ScreenshotService:
    @staticmethod
    def capture_screenshot():
        image = pyautogui.screenshot()
        buffer = io.BytesIO()
        image.save(
            buffer,
            format="PNG"
        )
        screenshot_data = base64.b64encode(
            buffer.getvalue()
        ).decode()  
        return screenshot_data
