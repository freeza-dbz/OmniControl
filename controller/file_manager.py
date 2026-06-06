import base64
import os

class FileManager:
    
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
