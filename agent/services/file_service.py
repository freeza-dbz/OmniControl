import os
import base64

class FileService:
    SAVE_DIRECTORY = "received_files"

    @staticmethod
    def save_file(filename, encoded_content):
        safe_filename = os.path.basename(filename)
        if not safe_filename:
            raise ValueError("Invalid filename")

        os.makedirs(
            FileService.SAVE_DIRECTORY, 
            exist_ok=True
        )
        
        base_dir = os.path.abspath(FileService.SAVE_DIRECTORY)
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
    
    @staticmethod
    def read_file(file_path):
        # Prevent accessing files outside of the project root
        # Note: since this service is under agent/services, project_root is 2 directories up
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        target_path = os.path.abspath(file_path)
        
        if not target_path.startswith(project_root):
            raise PermissionError("Path traversal detected - accessing files outside project root is forbidden")

        with open(target_path, "rb") as file:
            encoded_content = base64.b64encode(
                file.read()
            ).decode()
            
        return encoded_content
