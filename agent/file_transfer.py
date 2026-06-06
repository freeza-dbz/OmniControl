import os
import base64


class FileTransfer:
    
    SAVE_DIRECTORY = "received_files"
    
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
    
    @staticmethod
    def read_file(file_path):
        
        with open(file_path, "rb") as file:
            encoded_content = base64.b64encode(
                file.read()
                ).decode()
            
        return encoded_content