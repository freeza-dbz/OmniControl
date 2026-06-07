import socketio
import time
import threading


sio = socketio.Client()
online_agents = {}
operation_finished = threading.Event()


@sio.event
def connect():
    print("----------CONNECTED TO SERVER----------")

# command results

@sio.event
def command_result(data):
    try:
        time.sleep(0.5)
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
    finally:
        operation_finished.set()

# agents listing

@sio.event
def agents_update(data):
    
    global online_agents
    try:
        time.sleep(0.5)
        online_agents = data or {}
        
        print("\n----------ONLINE AGENTS UPDATE----------")
        if not data:
            print("No agents online.")
        else:
            print("Online agents:")
            for device_id, agent_info in online_agents.items():
                print(f"  - {device_id} ({agent_info.get('hostname', 'N/A')})")
        print("--------------------\n")
    finally:
        operation_finished.set()

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
    
    try:
        time.sleep(0.5)
        # result of file tranfer from server
        
        print("\n----------FILE UPLOAD----------")
        print(data)
        print("--------------------\n")
    finally:
        operation_finished.set()


# download file

from file_manager import FileManager

@sio.event
def download_result(data):
    try:
        time.sleep(0.5)
        if data.get("status") == "error":
            print("\n----------FILE DOWNLOAD ERROR----------")
            print(f"Error downloading '{data.get('filename', 'N/A')}': {data.get('message', 'Unknown error')}")
            print("--------------------\n")
            return
        
        filepath = FileManager.save_downloaded_file(
            data["filename"], data["content"]
        )
        
        print("\n----------FILE DOWNLOAD SUCCESS----------")
        print(f"File downloaded successfully to: {filepath}")
        print("--------------------\n")
    finally:
        operation_finished.set()
    
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
            operation_finished.clear()
            sio.emit("get_agents")
            operation_finished.wait(timeout=5.0)
            time.sleep(1)
            
        # Command Execution 
        
        elif choice == "2":
            
            target = input("Target Device ID: ")
            if not is_agent_available(target):
                continue
            
            while True:
                command = input(f"Command for '{target}': ")
                print("--> Executing command...")
                operation_finished.clear()
                sio.emit("execute_command", {"target": target, "command": command})
                print("--> Waiting for result...")
                operation_finished.wait()
                
                another = input(f"Execute another command on '{target}'? (y/n): ").lower()
                if another not in ['y', 'yes']:
                    break
            time.sleep(1)

        # File Transfer

        elif choice == "3":
            
            target = input("Target Device ID : ")
            if not is_agent_available(target):
                continue
            
            while True:
                filepath = input("File Path : ").strip(' "\'')
                print("--> Uploading file...")
                operation_finished.clear()
                upload_file(target, filepath)
                print("--> Waiting for result...")
                operation_finished.wait()
                
                another = input(f"Upload another file to '{target}'? (y/n): ").lower()
                if another not in ['y', 'yes']:
                    break
            time.sleep(1)
        
        # Download file
        
        elif choice == "4":
            target = input("Target Device ID : ")
            if not is_agent_available(target):
                continue
            
            while True:
                remote_filepath = input("Remote File Path : ").strip(' "\'')
                print("--> Requesting file download...")
                operation_finished.clear()
                request_file_download(target, remote_filepath)
                print("--> Waiting for download...")
                operation_finished.wait()

                another = input(f"Download another file from '{target}'? (y/n): ").lower()
                if another not in ['y', 'yes']:
                    break
            time.sleep(1)
        
        # Exit
        
        elif choice == "5":
            
            print("Disconnecting...")
            time.sleep(0.5)
            sio.disconnect()
            break
        
        else:
            print("Invalid choice, please try again.")
            time.sleep(1)
            
except KeyboardInterrupt:
    
    print("Disconnecting...")
    time.sleep(0.5)
    print("\nExiting...")
    
finally:
    
    if sio.connected:
        sio.disconnect()