import socketio

sio = socketio.Client()


@sio.event
def connect():
    print("CONNECTED TO SERVER")


@sio.event
def command_result(data):
    print("\n===== RESULT =====")
    print(data["output"])
    print("==================\n")


@sio.event
def disconnect():
    print("DISCONNECTED")


sio.connect("http://localhost:5000")

while True:
    target = input("Target Device ID: ")
    command = input("Command: ")

    sio.emit(
        "execute_command",
        {
            "target": target,
            "command": command
        }
    )