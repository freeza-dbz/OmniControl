import time
from shared.logger import get_logger
from controller.services.file_service import FileService
from controller.services.screenshot_service import ScreenshotService

logger = get_logger("client")

def register_event_handlers(sio, state):
    @sio.event
    def connect():
        logger.info("Client connected to server.")
        print("----------CONNECTED TO SERVER----------")

    @sio.event
    def command_result(data):
        try:
            time.sleep(0.5)
            logger.info(f"Received command result from agent {data.get('device_id', 'unknown')} for controller {data.get('controller_sid', 'unknown')}")
            print("\n----------COMMAND RESULT---------- \n")
            output = data.get("output")
            message = data.get("message")
            if output is not None:
                print(output)
            elif message is not None:
                print(f"Error : {message}")
            else:
                print(f"Received an unexpected result format: {data}")
            print("=====================\n")
        finally:
            state["operation_finished"].set()

    @sio.event
    def agents_update(data):
        try:
            time.sleep(0.5)
            state["online_agents"].clear()
            state["online_agents"].update(data or {})
            logger.info(f"Received agents update from server: {len(state['online_agents'])} agents online.")
            
            print("\n----------ONLINE AGENTS UPDATE----------")
            if not data:
                print("No agents online.")
            else:
                print("Online agents:")
                for device_id, agent_info in state["online_agents"].items():
                    print(f"  - {device_id} ({agent_info.get('hostname', 'N/A')})")
                print("=====================\n")
        finally:
            state["operation_finished"].set()

    @sio.event
    def disconnect():
        logger.info("Client disconnected from server.")

    @sio.event
    def upload_result(data):
        try:
            time.sleep(0.5)
            logger.info(f"Received file upload result from server for controller {data.get('controller_sid', 'unknown')}")
            print("\n----------FILE UPLOAD----------")
            print(data)
            print("=====================\n")
        finally:
            state["operation_finished"].set()

    @sio.event
    def download_result(data):
        try:
            time.sleep(0.5)
            logger.info(f"Received file download result from server for controller {data.get('controller_sid', 'unknown')}")
            if data.get("status") == "error":
                print("\n----------FILE DOWNLOAD ERROR----------")
                print(f"Error downloading '{data.get('filename', 'N/A')}': {data.get('message', 'Unknown error')}")
                print("=====================\n")
                return
            
            filepath = FileService.save_downloaded_file(
                data["filename"], data["content"]
            )
            print("\n----------FILE DOWNLOAD SUCCESS----------")
            print(f"File downloaded successfully to: {filepath}")
            print("=====================\n")
        finally:
            state["operation_finished"].set()

    @sio.event
    def screenshot_result(data):
        try:
            time.sleep(0.5)
            logger.info(f"Received screenshot result from server for controller {data.get('controller_sid', 'unknown')}")
            if data["status"] == "error":
                print("\n----------SCREENSHOT ERROR----------")
                print(f"ERROR: {data['message']}")
                print("=====================\n")
                return

            path = ScreenshotService.save_screenshot(data["image_data"])
            print("\n----------SCREENSHOT SAVED----------")
            print(f"Screenshot saved to: {path}")
            print("=====================\n")
        finally:
            state["operation_finished"].set()

    @sio.event
    def process_list(data):
        try:
            logger.info(f"Received process list from server for controller {data.get('controller_sid', 'unknown')}")
            print("\n---------- PROCESSES ----------")
            for proc in data["processes"][:30]:
                print(f"{proc['pid']} | {proc['name']}")
            print("=====================\n")
        finally:
            state["operation_finished"].set()

    @sio.event
    def kill_result(data):
        try:
            logger.info(f"Received kill process result from server for controller {data.get('controller_sid', 'unknown')}")
            print("\n---------- KILL RESULT ----------")
            print(data["message"])
            print("=======================\n")
        finally:
            state["operation_finished"].set()

    @sio.event
    def start_result(data):
        try:
            logger.info(f"Received start process result from server for controller {data.get('controller_sid', 'unknown')}")
            print("\n---------- START RESULT ----------")
            print(data["message"])
            print("========================\n")
        finally:
            state["operation_finished"].set()
