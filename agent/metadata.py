import socket
import platform
import getpass
import sys
import os

# Add the project root to sys.path to allow importing 'shared'
# This assumes metadata.py is located at OmniControl/agent/metadata.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from shared.auth import ( AGENT_TOKEN )

def get_agent_metadata(device_id: str) -> dict:
    
    return {
        "device_id": device_id,
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os": platform.system(),
        "token" : AGENT_TOKEN
    }