import time
import socketio
import os
import sys

# Add project root to sys.path to allow importing 'shared' and 'agent'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.logger import get_logger
from agent.handlers.event_handlers import register_event_handlers
from agent.services.metadata_service import AGENT_TOKEN

logger = get_logger("agent")

DEVICE_ID = "PC-001"
sio = socketio.Client()

# Register event handlers
register_event_handlers(sio, DEVICE_ID)

try:
    sio.connect("http://localhost:5000", auth={"token": AGENT_TOKEN, "type": "agent"})
    sio.wait()
except KeyboardInterrupt:
    print("\n Disconnecting from server.")
    time.sleep(0.5)
    print("\n Exiting... ")
    time.sleep(0.5)
finally:
    if sio.connected:
        sio.disconnect()
