import base64
import os
from datetime import datetime

class FileManager:
    
    # File transfer
    
    @staticmethod
    def prepare_upload(filepath):
        
        with open(
            filepath,
            "rb"
        ) as f:
            
            encode = base64.b64encode( 
                f.read()
            ).decode()
            
        return {
            "filename": os.path.basename(filepath),
            "content": encode
        }
    
    # File transfer - Save downloaded file
    
    @staticmethod
    def save_downloaded_file(filename, encoded_content):
        
        save_dir = "downloads"
        os.makedirs(
            save_dir, exist_ok=True
        )
        
        save_path = os.path.join(
            save_dir, filename
        )
        
        with open(
            save_path,
            "wb"
        ) as f:
            
            f.write(
                base64.b64decode(encoded_content)
            )
            
        return save_path
    
    # Screenshot handling
    
    @staticmethod
    def save_screenshot(encoded_content):
        
        os.makedirs(
            "screenshot",
            exist_ok=True
        )
        
        filename= (
            datetime.now()
            .strftime("%Y-%m-%d_%H-%M-%S")
            +".png"
        )
        
        path = os.path.join(
            "screenshot",
            filename
        )
        
        with open( path, "wb") as f:
            f.write(
                base64.b64decode(encoded_content)
            )
            
        return path
