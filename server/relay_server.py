import socketio
import eventlet
import eventlet.wsgi
import os
import sys
import functools

# Add project root to sys.path to allow importing 'shared'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from server.agent_registry import AgentRegistry
from server.services.agent_service import AgentService
from shared.logger import get_logger

logger = get_logger("server")

sio = socketio.Server(
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

app = socketio.WSGIApp(sio)
agent_registry = AgentRegistry()
agent_service = AgentService(sio, agent_registry)

def require_role(required_role):
    def decorator(handler):
        @functools.wraps(handler)
        def wrapper(sid, *args, **kwargs):
            session = sio.get_session(sid)
            if not session or session.get("role") != required_role:
                print(f"Access Denied for {sid}: Needs {required_role} role")
                if required_role == "controller":
                    sio.emit("error", {"message": "Unauthorized: Controller access required"}, to=sid)
                return
            return handler(sid, *args, **kwargs)
        return wrapper
    return decorator

# Import and register handlers
from server.handlers.auth_handler import register_auth_handlers
from server.handlers.agent_handler import register_agent_handlers
from server.handlers.command_handler import register_command_handlers
from server.handlers.file_handler import register_file_handlers
from server.handlers.screenshot_handler import register_screenshot_handlers
from server.handlers.process_handler import register_process_handlers
from server.handlers.heartbeat_handler import register_heartbeat_handlers

register_auth_handlers(sio, agent_registry, require_role, agent_service)
register_agent_handlers(sio, agent_registry, require_role, agent_service)
register_command_handlers(sio, agent_registry, require_role, agent_service)
register_file_handlers(sio, agent_registry, require_role, agent_service)
register_screenshot_handlers(sio, agent_registry, require_role, agent_service)
register_process_handlers(sio, agent_registry, require_role, agent_service)
register_heartbeat_handlers(sio, agent_registry, require_role, agent_service)

if __name__ == "__main__":
    print("----------Relay server started on port 5000----------")

    eventlet.wsgi.server(
        eventlet.listen(("0.0.0.0", 5000)),
        app
    )