import os
import base64
import io 
import pyautogui


class FileTransfer:
    
    SAVE_DIRECTORY = "received_files"
    
    # File transfer
    
    @staticmethod
    def save_file(filename, encoded_content):
        # Extract only the base name to prevent directory traversal
        safe_filename = os.path.basename(filename)
        if not safe_filename:
            raise ValueError("Invalid filename")

        os.makedirs(
            FileTransfer.SAVE_DIRECTORY, 
            exist_ok=True
        )
        
        # Build path and verify it is strictly within SAVE_DIRECTORY
        base_dir = os.path.abspath(FileTransfer.SAVE_DIRECTORY)
        file_path = os.path.abspath(os.path.join(base_dir, safe_filename))
        
        if not file_path.startswith(base_dir):
            raise PermissionError("Path traversal detected")
            
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
        # Prevent accessing files outside of the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        target_path = os.path.abspath(file_path)
        
        if not target_path.startswith(project_root):
            raise PermissionError("Path traversal detected - accessing files outside project root is forbidden")

        with open(target_path, "rb") as file:
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