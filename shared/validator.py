import os
import re

class Validator:
    
    @staticmethod
    def validate_device_id(device_id: str) -> bool:
        
        if not isinstance(device_id, str):
            return False
        
        if len(device_id.strip()) == 0:
            return False
        
        return True
        
        
    @staticmethod
    def validate_command(command: str) -> bool:
        
        if not isinstance(command, str):
            return False
        
        if (len(command.strip()) == 0 or
            len(command) > 1024 or
            re.search(r'[<>:"/\\|?*]', command)
        ):
            return False
        
        return True
    
    @staticmethod
    def validate_pid(pid) -> bool:
        
        try:
            pid = int(pid)
            return pid > 0
        
        except ValueError:
            return False
        
    @staticmethod
    def validate_filename(filename: str) -> bool:
        
        if not isinstance(filename, str):
            return False
        
        if (len(filename.strip()) == 0 or
            len(filename) > 255 or
            re.search(r'[<>:"/\\|?*]', filename)
        ):
            return False
        
        return True
    
    @staticmethod
    def validate_filepath(filepath: str) -> bool:
        
        if not isinstance(filepath, str):
            return False
        
        normalized = os.path.normpath(filepath)

        if ".." in normalized:
            return False
        
        if (len(filepath.strip()) == 0 or
            len(filepath) > 4096 or
            re.search(r'[<>:"|?*]', filepath)
        ):
            return False
        
        return True
    
    @staticmethod
    def validate_sid(sid: str) -> bool:
        
        if not isinstance(sid, str):
            return False
        
        if (len(sid.strip()) == 0 or
            len(sid) > 255 or
            re.search(r'[<>:"/\\|?*]', sid)
        ):
            return False
        
        return True
    
    @staticmethod
    def validate_base64_content(content: str) -> bool:
        
        if not isinstance(content, str):
            return False
        
        if len(content.strip()) == 0:
            return False
        
        try:
            import base64
            base64.b64decode(content, validate=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_token(token: str) -> bool:
        
        if not isinstance(token, str):
            return False
        
        if (len(token.strip()) == 0 or
            len(token) > 255 or
            re.search(r'[<>:"/\\|?*]', token)
        ):
            return False
        
        return True 