import time
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from controller.websocket_client import connect, disconnect, sio, online_agents, operation_finished
from controller.services.command_service import CommandService
from controller.services.file_service import FileService
from controller.services.screenshot_service import ScreenshotService
from controller.services.process_service import ProcessService

def is_agent_available(target_id: str) -> bool:
    if target_id not in online_agents:
        print(f"\nError: Device '{target_id}' not found or offline.")
        time.sleep(1)
        return False
    return True

def main():
    try:
        connect()
        while True:
            print("\n1. List Devices")
            print("2. Execute Command")
            print("3. File Transfer")
            print("4. Download File")
            print("5. Request Screenshot")
            print("6. Process Management")
            print("7. Exit")
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
                    CommandService.execute_command(sio, target, command)
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
                    FileService.upload_file(sio, target, filepath)
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
                    FileService.request_file_download(sio, target, remote_filepath)
                    print("--> Waiting for download...")
                    operation_finished.wait()

                    another = input(f"Download another file from '{target}'? (y/n): ").lower()
                    if another not in ['y', 'yes']:
                        break
                time.sleep(1)
                
            # Request Screenshot
            elif choice == "5":
                target = input("Target Device ID : ")
                if not is_agent_available(target):
                    continue
                
                print("--> Requesting screenshot...")
                operation_finished.clear()
                ScreenshotService.request_screenshot(sio, target)
                print("--> Waiting for screenshot...")
                operation_finished.wait()
                time.sleep(1)
                
            # Process management
            elif choice == "6":
                target = input("Target Device ID : ")
                if not is_agent_available(target):
                    continue
                
                while True:
                    print("\nProcess Management Options:")
                    print("1. List Processes")
                    print("2. Kill Process")
                    print("3. Start Process")
                    print("4. Back to Main Menu")
                    pm_choice = input("Choice: ")

                    if pm_choice == "1":
                        print("--> Requesting process list...")
                        operation_finished.clear()
                        ProcessService.request_processes(sio, target)
                        print("--> Waiting for process list...")
                        operation_finished.wait()

                    elif pm_choice == "2":
                        pid = input("Process ID to kill: ")
                        print(f"--> Requesting to kill process {pid}...")
                        operation_finished.clear()
                        ProcessService.kill_remote_process(sio, target, pid)
                        print("--> Waiting for kill result... (Returning to main menu)")
                        operation_finished.wait()
                        break # Go back to main menu after killing

                    elif pm_choice == "3":
                        command = input("Command to start process: ")
                        print(f"--> Requesting to start process with command '{command}'...")
                        operation_finished.clear()
                        ProcessService.start_remote_process(sio, target, command)
                        print("--> Waiting for start result... (Returning to main menu)")
                        operation_finished.wait()
                        break # Go back to main menu after starting

                    elif pm_choice == "4":
                        break

                    else:
                        print("Invalid choice, please try again.")
                        time.sleep(1)
                time.sleep(1)
            
            # Exit 
            elif choice == "7":
                print("Disconnecting...")
                time.sleep(0.5)
                disconnect()
                break
            
            else:
                print("Invalid choice, please try again.")
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("Disconnecting...")
        time.sleep(0.5)
        print("\nExiting...")
    finally:
        disconnect()

if __name__ == "__main__":
    main()
