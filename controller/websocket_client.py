import socketio
import threading
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.auth import CONTROLLER_TOKEN
from controller.handlers.event_handlers import register_event_handlers

sio = socketio.Client()
online_agents = {}
operation_finished = threading.Event()

state = {
    "online_agents": online_agents,
    "operation_finished": operation_finished
}

# Register event handlers
register_event_handlers(sio, state)

def connect():
    sio.connect("http://localhost:5000", auth={"token": CONTROLLER_TOKEN, "type": "controller"})

def disconnect():
    if sio.connected:
        sio.disconnect()
