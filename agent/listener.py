import os

import socketio
import subprocess
import threading
import time


DEVICE_ID = "PC-001"
HEARTBEAT_INTERVAL = 5  # seconds
 
sio = socketio.Client()

# connecting to server

from metadata import get_agent_metadata

@sio.event
def connect():
    print("----------CONNECTED TO SERVER----------")

    sio.emit(
        "register_agent", get_agent_metadata(DEVICE_ID)
    )
    
    # Start sending heartbeats in a background thread
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

def send_heartbeat():
    """Sends a heartbeat to the server at regular intervals."""
    while sio.connected:
        time.sleep(HEARTBEAT_INTERVAL)
        sio.emit("heartbeat", {"device_id": DEVICE_ID})
        

@sio.event
def registration_success(data):
    print("----------REGISTERED----------", data)

# executing command 

@sio.event
def run_command(data):
    command = data["command"]
    controller_sid = data["controller_sid"]

    print("----------COMMAND----------", command)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        output = result.stdout

        if result.stderr:
            output += "\n" + result.stderr

        sio.emit(
            "command_result",
            {
                "controller_sid": controller_sid,
                "status": "success",
                "output": output
            }
        )

    except Exception as e:
        sio.emit(
            "command_result",
            {
                "controller_sid": controller_sid,
                "status": "error",
                "output": str(e)
            }
        )
        

# file transfer
    
from file_transfer import FileTransfer

@sio.event
def upload_file(data):
    controller_sid = data.get("controller_sid")
    response = {"controller_sid": controller_sid}
    try:
        
        filepath = FileTransfer.save_file(
            data["filename"], 
            data["content"]
        )
        
        print("----------FILE TRANSFER----------")
        
        print("File Received : ",  filepath)
        
        response.update({
            "status" : "success",
            "filename" : data["filename"]
        })
        sio.emit(
            "upload_result",
            response
        )
        
    except Exception as e:
        response.update({
            "status": "error",
            "message": str(e)
        })
        sio.emit(
            "upload_result",
            response
        )


# Download file

from file_transfer import FileTransfer

@sio.event
def download_file(data):
    try:

        filepath = data["filename"]

        encoded_content = FileTransfer.read_file(
            filepath
        )
        
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

# Screenshot capture

from file_transfer import FileTransfer

@sio.event
def screenshot(data):
    
    try:
         
        encoded_screenshot = FileTransfer.capture_screenshot()
        
        sio.emit(
            "screenshot_result",
            {
                "controller_sid" :  data["controller_sid"],
                "status" : "success",
                "image_data" : encoded_screenshot
            }
        )
        
    except Exception as e:
        
        sio.emit(
            "screenshot_result",
            {
                "controller_sid" :  data["controller_sid"],
                "status" : "error",
                "message" : str(e)
            }
        )


#  Process management

from process_manager import ProcessManager

@sio.event
def get_processes(data):
    
    # List Of processes
    
    processes = (
        ProcessManager
        .list_processes()
    )

    sio.emit(
        "process_list",
        {
            "controller_sid":
                data["controller_sid"],
            "processes":
                processes
        }
    )
    
@sio.event
def kill_process(data):
    
    # Kill process 
    
    result = (
        ProcessManager
        .kill_process(
            data["pid"]
        )
    )

    result["controller_sid"] = (
        data["controller_sid"]
    )

    sio.emit(
        "kill_result",
        result
    )
    

@sio.event
def start_process(data):

    # Start process
        
    result = (
        ProcessManager
        .start_process(
            data["command"]
        )
    )

    result["controller_sid"] = (
        data["controller_sid"]
    )

    sio.emit(
        "start_result",
        result
    )
    
    
        


# server connection 

@sio.event
def disconnect():
    print("----------DISCONNECTED----------")


try:
    from metadata import AGENT_TOKEN
    sio.connect("http://localhost:5000", auth={"token": AGENT_TOKEN, "type": "agent"})
    sio.wait()
except KeyboardInterrupt:
    print("\n Disconnecting from server.")
    time.sleep(0.5)
    print("\n Exiting... ")
    time.sleep(0.5)
finally:
    if sio.connected:
        sio.disconnect()
