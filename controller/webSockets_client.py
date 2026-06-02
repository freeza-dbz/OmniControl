import socketio

sio = socketio.Client()


@sio.event
def connect():
    print("----------CONNECTED TO SERVER----------")


@sio.event
def command_result(data):
    print("\n----------COMMAND RESULT----------")
    print(data["output"])
    print("--------------------\n")


@sio.event
def agents_update(data):
    print("\n----------ONLINE AGENTS UPDATE----------")
    if not data:
        print("No agents online.")
    else:
        print("Online agents:")
        for device_id, agent_info in data.items():
            print(f"  - {device_id} ({agent_info.get('hostname', 'N/A')})")
    print("--------------------\n")


@sio.event
def disconnect():
    print("----------DISCONNECTED----------")


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