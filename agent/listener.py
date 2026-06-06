import socketio
import subprocess
import time



DEVICE_ID = "PC-001"

sio = socketio.Client()

# connecting to server

from metadata import get_agent_metadata

@sio.event
def connect():
    print("----------CONNECTED TO SERVER----------")

    sio.emit(
        "register_agent", get_agent_metadata(DEVICE_ID)
    )


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
        

# server connection 

@sio.event
def disconnect():
    print("----------DISCONNECTED----------")


try:
    sio.connect("http://localhost:5000")
    sio.wait()
except KeyboardInterrupt:
    print("\n Disconnecting from server.")
    time.sleep(0.5)
    print("\n Exiting... ")
    time.sleep(0.5)
finally:
    if sio.connected:
        sio.disconnect()
