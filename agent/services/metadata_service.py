import socket
import platform
import getpass
import os
import sys

# project_root relative to agent/services/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.auth import AGENT_TOKEN

def get_agent_metadata(device_id: str) -> dict:
    return {
        "device_id": device_id,
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os": platform.system(),
        "token": AGENT_TOKEN
    }
