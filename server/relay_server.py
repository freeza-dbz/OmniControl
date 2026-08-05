import socketio
import eventlet
import eventlet.wsgi
import os
import sys


from agent_registry import AgentRegistry
from shared.auth import AGENT_TOKEN, CONTROLLER_TOKEN


from shared.logger import get_logger
logger = get_logger("server")


from shared.validator import Validator


# Add project root to sys.path to allow importing 'shared'

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)



sio = socketio.Server(
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

app = socketio.WSGIApp(sio)

agent_registry = AgentRegistry()

def _get_public_agents():
    
    # Returns a dictionary of agents safe for public consumption.
    
    return agent_registry.get_public_list()

def broadcast_agent_update():
    print("--------Broadcasting the current list of agents to all clients.------")
    public_agents = _get_public_agents()
    sio.emit("agents_update", public_agents)

# client connection
import functools

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

@sio.event
def connect(sid, environ, auth=None):
    
    logger.info(f"Client attempting to connect: {sid}")
    token = auth.get("token")
    
    if not Validator.validate_token(token):
        sio.disconnect(sid)
        return
    
    if not Validator.validate_sid(sid):
        sio.disconnect(sid)
        return
    
    
    print("----------CLIENT CONNECTED----------", sid)
    if not auth or not isinstance(auth, dict):
        print(f"Connection refused for {sid}: No authentication provided.")
        raise socketio.exceptions.ConnectionRefusedError("Authentication required")

    client_type = auth.get("type")

    if client_type == "agent":
        if token != AGENT_TOKEN:
            print(f"Connection refused for agent {sid}: Invalid token.")
            raise socketio.exceptions.ConnectionRefusedError("Invalid agent token")
        print(f"Agent authenticated: {sid}")
        sio.save_session(sid, {"role": "agent"})
    elif client_type == "controller":
        if token != CONTROLLER_TOKEN:
            print(f"Connection refused for controller {sid}: Invalid token.")
            raise socketio.exceptions.ConnectionRefusedError("Invalid controller token")
        print(f"Controller authenticated: {sid}")
        sio.save_session(sid, {"role": "controller"})
    else:
        print(f"Connection refused for {sid}: Unknown client type {client_type}")
        raise socketio.exceptions.ConnectionRefusedError("Invalid client type")

    public_agents = _get_public_agents()
    sio.emit("agents_update", public_agents, to=sid)


@sio.event
def disconnect(sid):
    
    logger.info(f"Client disconnected: {sid}")
    
    print("----------CLIENT DISCONNECTED----------", sid)
    device_to_remove = agent_registry.remove(sid)
    if device_to_remove:
        print("----------AGENT REMOVED----------", device_to_remove)
        broadcast_agent_update()

# agent registeration

@sio.event
@require_role("agent")
def register_agent(sid, data):
    device_id = agent_registry.register(sid, data)
    
    if not Validator.validate_device_id(device_id):
        return
    
    
    logger.info(f"Agent registered: {device_id} from {sid}")
    
    print("----------AGENT REGISTERED----------", device_id)
    
    print("\n=== AGENT REGISTERED ===")
    print(f"Device ID : {data['device_id']}")
    print(f"Hostname  : {data['hostname']}")
    print(f"Username  : {data['username']}")
    print(f"OS        : {data['os']}")
    print("========================\n")

    sio.emit(
        "registration_success",
        {"device_id": device_id},
        to=sid
    )
    broadcast_agent_update()

@sio.event
@require_role("controller")
def get_agents(sid):
    
    # Handles a request from a controller to get the current agent list.
    
    logger.info(f"Client {sid} requested agent list.")
    
    print(f"----------Client {sid} requested agent list.----------")
    public_agents = _get_public_agents()
    sio.emit("agents_update", public_agents, to=sid)


# forwarding command to agent

@sio.event
@require_role("controller")
def execute_command(sid, data):
    target = data["target"]
    command = data["command"]
    
    if not Validator.validate_device_id(target):
        return
    
    if not Validator.validate_command(command):
        return

    if not agent_registry.is_agent_online(target):
        sio.emit(
            "command_result",
            {
                "status": "error",
                "message": f"Agent '{target}' not found or is offline."
            },
            to=sid
        )
        return

    target_sid = agent_registry.get_sid(target)

    sio.emit(
        "run_command",
        {
            "controller_sid": sid,
            "command": command
        },
        to=target_sid
    )

 
@sio.event
@require_role("agent")
def command_result(sid, data):

# forwarding command results back to controller

    logger.info(f"Agent {sid} sent command result to controller {data['controller_sid']}")

    controller_sid = data["controller_sid"]

    sio.emit(
        "command_result",
        data,
        to=controller_sid
    ) 

#file transfer

@sio.event
@require_role("controller")
def upload_file(sid, data):
   
    target = data["target"]
    
    if not Validator.validate_device_id(target):
        return
    
    if not Validator.validate_filename(data.get("filename", "")):
        return
    
    if not Validator.validate_filepath(data.get("filepath", "")):
        return
    
    if not Validator.validate_base64_content(data.get("content", "")):
        return
    
    if not agent_registry.is_agent_online(target):
        sio.emit(
            "upload_result",
            {
                "status" : "error",
                "message": f"Agent '{target}' not found or is offline."
            },
            to=sid
        )
        
        return 
    
    target_sid = agent_registry.get_sid(target)
    
    # Add controller SID for response routing
    data['controller_sid'] = sid
    
    sio.emit(
        "upload_file",
        data,
        to=target_sid
    )


@sio.event
@require_role("agent")
def upload_result(sid, data):

# Forwarding Transfer file result back to controller

    logger.info(f"Agent {sid} sent upload result to controller {data.get('controller_sid', 'unknown')}")

    controller_sid = data.get("controller_sid")
    if controller_sid:
        sio.emit("upload_result", data, to=controller_sid)
    else:
        print(f"Warning: Received 'upload_result' from agent {sid} without a 'controller_sid'. Cannot forward.")
    
# Download file 

@sio.event
@require_role("controller")
def download_file(sid, data):
    
    target = data["target"]
    filename = data.get("filename")
    
    if not Validator.validate_device_id(target):
        return
    
    if not Validator.validate_filename(filename):
        return
    
    if not Validator.validate_filepath(data.get("filepath", "")):
        return
    
    
    if not agent_registry.is_agent_online(target):
        sio.emit(
            "download_result",
            {
                "status": "error",
                "message": f"Agent '{target}' not found or is offline.",
                "filename": filename or "N/A"
            },
            to=sid
        )
        return 
    
    target_sid = agent_registry.get_sid(target)
    
    sio.emit(
        "download_file",
        {
            "controller_sid": sid,
            "filename": filename
        },
        to=target_sid
    )
    
    
@sio.event
@require_role("agent")
def download_result(sid, data):
    
    # Forwarding Download file result back to controller
    
    logger.info(f"Agent {sid} sent download result to controller {data.get('controller_sid', 'unknown')}")  
    controller_sid = data["controller_sid"]

    sio.emit(
        "download_result",
        data,
        to=controller_sid
    )
  
    # screenshot
    
# Screenshot

@sio.event()
@require_role("controller")
def screenshot(sid, data):
    
    target = data["target"]
    
    if not Validator.validate_device_id(target):
        return


    if not agent_registry.is_agent_online(target):
        sio.emit(
            "screenshot_result",
            {
                "status": "error",
                "message": f"Agent '{target}' not found or is offline."
            },
            to=sid
        )
        return 
    
    target_sid = agent_registry.get_sid(target)
    
    # Add controller SID for response routing
    
    data['controller_sid'] = sid
    
    sio.emit(
        "screenshot",
        data,
        to=target_sid
    )
    
@sio.event()
@require_role("agent")
def screenshot_result(sid, data):
    
    # Forwarding Screenshot result back to controller
    
    logger.info(f"Agent {sid} sent screenshot result to controller {data.get('controller_sid', 'unknown')}")
    
    controller_sid = data.get("controller_sid")
    if controller_sid:
        sio.emit("screenshot_result", data, to=controller_sid)
    else:
        print(f"Warning: Received 'screenshot_result' from agent {sid} without a 'controller_sid'. Cannot forward.")


# Process management

@sio.event
@require_role("controller")
def get_processes(sid, data):
    
    # Get Process list

    target = data["target"]
    
    if not Validator.validate_device_id(target):
        return
    

    if not agent_registry.is_agent_online(target):
        sio.emit(
            "process_list",
            {
                "controller_sid": sid,
                "status": "error",
                "message": f"Agent '{target}' is offline.",
                "processes": []
            },
            to=sid
        )
        return

    target_sid = agent_registry.get_sid(target)

    sio.emit(
        "get_processes",
        {
            "controller_sid": sid
        },
        to=target_sid
    )
    
@sio.event
@require_role("agent")
def process_list(sid, data):

    # Forwarding Process list back to controller

    sio.emit(
        "process_list",
        data,
        to=data["controller_sid"]
    )


@sio.event
@require_role("controller")
def kill_process(sid, data):
    
    # Kill process

    target = data["target"]
    
    if not Validator.validate_device_id(target):
        return
    
    if not Validator.validate_pid(data.get("pid")):
        return
    

    if not agent_registry.is_agent_online(target):
        sio.emit(
            "kill_result",
            {
                "status": "error",
                "message": f"Agent '{target}' is offline."
            },
            to=sid
        )
        return

    target_sid = agent_registry.get_sid(target)

    sio.emit(
        "kill_process",
        {
            "controller_sid": sid,
            "pid": data["pid"]
        },
        to=target_sid
    )
    
@sio.event
@require_role("agent")
def kill_result(sid, data):

# Forwarding Kill process result back to controller

    logger.info(f"Agent {sid} sent kill result to controller {data.get('controller_sid', 'unknown')}")

    sio.emit(
        "kill_result",
        data,
        to=data["controller_sid"]
    )
    

@sio.event
@require_role("controller")
def start_process(sid, data):
    
    # Start process

    logger.info(f"Controller {sid} requested to start process '{data['command']}' on agent '{data['target']}'")
    
    target = data["target"]
    
    if not Validator.validate_device_id(target):
        return
    
    if not Validator.validate_command(data.get("command")):
        return
    
    if not agent_registry.is_agent_online(target):
        sio.emit(
            "start_result",
            {
                "status": "error",
                "message": f"Agent '{target}' is offline."
            },
            to=sid
        )
        return

    target_sid = agent_registry.get_sid(target)

    sio.emit(
        "start_process",
        {
            "controller_sid": sid,
            "command": data["command"]
        },
        to=target_sid
    )    

@sio.event
@require_role("agent")
def start_result(sid, data):
    
    # Forwarding Start process result back to controller
    
    logger.info(f"Agent {sid} sent start process result to controller {data.get('controller_sid', 'unknown')}")

    sio.emit(
        "start_result",
        data,
        to=data["controller_sid"]
    )



    

if __name__ == "__main__":
    print("----------Relay server started on port 5000----------")

    eventlet.wsgi.server(
        eventlet.listen(("0.0.0.0", 5000)),
        app
    )