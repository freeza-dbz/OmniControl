import socketio
import time

sio = socketio.Client()


@sio.event
def connect():
    print("----------CONNECTED TO SERVER----------")

# command results

@sio.event
def command_result(data):
    print("\n----------COMMAND RESULT---------- \n")
    output = data.get("output")
    message = data.get("message")
    if output is not None:
        print(output)
    elif message is not None:
        print(f"Error : {message}")
    else:
        print(f"Received an unexpected result format: {data}")
    print("--------------------\n")

# agents listing

@sio.event
def agents_update(data):
    
    global online_agents
    online_agents = data or {}
    
    print("\n----------ONLINE AGENTS UPDATE----------")
    if not data:
        print("No agents online.")
    else:
        print("Online agents:")
        for device_id, agent_info in online_agents.items():
            print(f"  - {device_id} ({agent_info.get('hostname', 'N/A')})")
    print("--------------------\n")

# server connection

@sio.event
def disconnect():
    print("----------DISCONNECTED----------")


sio.connect("http://localhost:5000")

try:
    while True:
        print("\n1. List Devices")
        print("2. Execute Command")
        print("3. Exit")
        choice = input("Choice: ")

        if choice == "1":
            print("--> Requesting agent list...")
            sio.emit("get_agents")
            time.sleep(1)  
        elif choice == "2":
            target = input("Target Device ID: ")
            if target not in online_agents:
                time.sleep(0.5)
                print(f"Device '{target}' not found or offline.")
                continue
            command = input("Command: ")
            print("--> Executing command...")
            time.sleep(0.5)
            sio.emit("execute_command", {"target": target, "command": command})
        elif choice == "3":
            sio.disconnect()
            break
        else:
            print("Invalid choice, please try again.")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    print("disconnecting...")
    if sio.connected:
        sio.disconnect()