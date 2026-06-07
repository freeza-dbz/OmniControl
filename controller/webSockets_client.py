import socketio
import time


sio = socketio.Client()
online_agents = {}


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
    print("\n----------DISCONNECTED----------")


sio.connect("http://localhost:5000")

# file manager

from file_manager import FileManager

def upload_file(target, filepath):

    payload = FileManager.prepare_upload(filepath)

    payload["target"] = target
    
    sio.emit(
        "upload_file",
        payload
    )
    
@sio.event
def upload_result(data):
    
    # result of file tranfer from server
    
    print("\n----------FILE UPLOAD----------")
    
    print(data)
    
    print("--------------------\n")


# download file

from file_manager import FileManager

@sio.event
def download_result(data):
    if data["status"] == "error":
        
        print("\n----------FILE DOWNLOAD ERROR----------")
        print(f"Error downloading '{data['filename']}': {data['message']}") 
        
        return
    
    filepath = FileManager.save_downloaded_file(
        data["filename"], data["content"]
    )
    
    print("\n----------FILE DOWNLOAD SUCCESS----------")
    print(f"File downloaded successfully to: {filepath}")
    
    
def request_file_download(target, remote_filepath):
    
    # request file download from server
    
    sio.emit(
        "download_file",
        {
            "target": target,
            "filename": remote_filepath
        }
    )

    

# menu

def is_agent_available(target_id: str) -> bool:
    if target_id not in online_agents:
        print(f"\nError: Device '{target_id}' not found or offline.")
        time.sleep(1)
        return False
    return True


try:
    while True:
        print("\n1. List Devices")
        print("2. Execute Command")
        print("3. File Transfer")
        print("4. Download File")
        print("5. Exit")
        choice = input("Choice: ")

        if choice == "1":
            
            print("--> Requesting agent list...")
            sio.emit("get_agents")
            time.sleep(1)  
        
        elif choice == "2":
            
            target = input("Target Device ID: ")
            if not is_agent_available(target):
                continue
            
            while True:
                command = input(f"Command for '{target}': ")
                print("--> Executing command...")
                time.sleep(1)
                sio.emit("execute_command", {"target": target, "command": command})

                another = input(f"Execute another command on '{target}'? (y/n): ").lower()
                if another not in ['y', 'yes']:
                    break

        elif choice == "3":
            
            target = input("Target Device ID : ")
            if not is_agent_available(target):
                continue
            
            while True:
                filepath = input("File Path : ").strip(' "\'')
                print("--> Uploading file...")
                time.sleep(1)
                upload_file(target, filepath)
                
                another = input(f"Execute another command on '{target}'? (y/n): ").lower()
                if another not in ['y', 'yes']:
                    break
        
        elif choice == "4":
            target = input("Target Device ID : ")
            if not is_agent_available(target):
                continue
            
            remote_filepath = input("Remote File Path : ").strip(' "\'')
            print("--> Requesting file download...")
            time.sleep(1)
            request_file_download(target, remote_filepath)
        
        elif choice == "5":
            
            print("Disconnecting...")
            time.sleep(0.5)
            sio.disconnect()
            break
        
        else:
            print("Invalid choice, please try again.")
            
except KeyboardInterrupt:
    
    print("Disconnecting...")
    time.sleep(0.5)
    print("\nExiting...")
    
finally:
    
    if sio.connected:
        sio.disconnect()