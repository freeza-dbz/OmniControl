import base64
import os

class FileService:
    @staticmethod
    def prepare_upload(filepath):
        with open(filepath, "rb") as f:
            encode = base64.b64encode(f.read()).decode()
        return {
            "filename": os.path.basename(filepath),
            "content": encode
        }

    @staticmethod
    def save_downloaded_file(filename, encoded_content):
        save_dir = "downloads"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        with open(save_path, "wb") as f:
            f.write(base64.b64decode(encoded_content))
        return save_path

    @staticmethod
    def upload_file(sio, target, filepath):
        payload = FileService.prepare_upload(filepath)
        payload["target"] = target
        sio.emit("upload_file", payload)

    @staticmethod
    def request_file_download(sio, target, remote_filepath):
        sio.emit(
            "download_file",
            {
                "target": target,
                "filename": remote_filepath
            }
        )
