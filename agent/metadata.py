import socket
import platform
import getpass

def get_agent_metadata(device_id: str) -> dict:
    """
    Gathers and returns a dictionary of agent metadata.
    """
    return {
        "device_id": device_id,
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os": platform.system(),
    }