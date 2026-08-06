import os
from shared.logger import get_logger
from agent.services.metadata_service import get_agent_metadata
from agent.services.command_service import CommandService
from agent.services.file_service import FileService
from agent.services.screenshot_service import ScreenshotService
from agent.services.process_service import ProcessService
from agent.services.heartbeat_service import HeartbeatService

logger = get_logger("agent")

def register_event_handlers(sio, device_id):
    @sio.event
    def connect():
        logger.info("Connected to server.")
        print("----------CONNECTED TO SERVER----------")
        sio.emit("register_agent", get_agent_metadata(device_id))
        
        # Start sending heartbeats in a background thread
        heartbeat_service = HeartbeatService(sio, device_id)
        heartbeat_service.start()

    @sio.event
    def registration_success(data):
        print("----------REGISTERED----------", data)

    @sio.event
    def run_command(data):
        command = data["command"]
        controller_sid = data["controller_sid"]
        logger.info(f"Executing command from controller {controller_sid}: {command}")
        print("----------COMMAND----------", command)

        res = CommandService.run_command(command)
        res["controller_sid"] = controller_sid
        sio.emit("command_result", res)

    @sio.event
    def upload_file(data):
        controller_sid = data.get("controller_sid")
        response = {"controller_sid": controller_sid}
        try:
            filepath = FileService.save_file(
                data["filename"], 
                data["content"]
            )
            logger.info(f"File received from controller {controller_sid}: {filepath}")
            print("----------FILE TRANSFER----------")
            print("File Received : ",  filepath)
            
            response.update({
                "status": "success",
                "filename": data["filename"]
            })
            sio.emit("upload_result", response)
        except Exception as e:
            response.update({
                "status": "error",
                "message": str(e)
            })
            sio.emit("upload_result", response)

    @sio.event
    def download_file(data):
        try:
            filepath = data["filename"]
            encoded_content = FileService.read_file(filepath)
            logger.info(f"File sent to controller {data['controller_sid']}: {filepath}")
            sio.emit(
                "download_result",
                {
                    "controller_sid": data["controller_sid"],
                    "filename": os.path.basename(filepath),
                    "status": "success",
                    "content": encoded_content
                }
            )
        except Exception as e:
            sio.emit(
                "download_result",
                {
                    "controller_sid": data["controller_sid"],
                    "filename": os.path.basename(data.get("filename", "unknown file")),
                    "status": "error",
                    "message": str(e)
                }
            )

    @sio.event
    def screenshot(data):
        try:
            encoded_screenshot = ScreenshotService.capture_screenshot()
            logger.info(f"Screenshot captured and sent to controller {data['controller_sid']})")
            print("----------SCREENSHOT----------")
            sio.emit(
                "screenshot_result",
                {
                    "controller_sid": data["controller_sid"],
                    "status": "success",
                    "image_data": encoded_screenshot
                }
            )
        except Exception as e:
            sio.emit(
                "screenshot_result",
                {
                    "controller_sid": data["controller_sid"],
                    "status": "error",
                    "message": str(e)
                }
            )

    @sio.event
    def get_processes(data):
        processes = ProcessService.list_processes()
        logger.info(f"Process list sent to controller {data['controller_sid']}")
        sio.emit(
            "process_list",
            {
                "controller_sid": data["controller_sid"],
                "processes": processes
            }
        )

    @sio.event
    def kill_process(data):
        logger.info(f"Attempting to kill process {data['pid']} from controller {data['controller_sid']}")
        result = ProcessService.kill_process(data["pid"])
        result["controller_sid"] = data["controller_sid"]
        sio.emit("kill_result", result)

    @sio.event
    def start_process(data):
        logger.info(f"Attempting to start process '{data['command']}' from controller {data['controller_sid']}")
        result = ProcessService.start_process(data["command"])
        result["controller_sid"] = data["controller_sid"]
        sio.emit("start_result", result)

    @sio.event
    def disconnect():
        logger.info("Disconnected from server.")
        print("----------DISCONNECTED----------")
