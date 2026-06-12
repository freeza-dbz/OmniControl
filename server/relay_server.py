import socketio
import eventlet
import eventlet.wsgi
from agent_registry import AgentRegistry


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

@sio.event
def connect(sid, environ):
    print("----------CLIENT CONNECTED----------", sid)
    public_agents = _get_public_agents()
    sio.emit("agents_update", public_agents, to=sid)


@sio.event
def disconnect(sid):
    print("----------CLIENT DISCONNECTED----------", sid)
    device_to_remove = agent_registry.remove(sid)
    if device_to_remove:
        print("----------AGENT REMOVED----------", device_to_remove)
        broadcast_agent_update()

# agent registeration

@sio.event
def register_agent(sid, data):
    device_id = agent_registry.register(sid, data)
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
def get_agents(sid):
    
    # Handles a request from a controller to get the current agent list.
    
    print(f"----------Client {sid} requested agent list.----------")
    public_agents = _get_public_agents()
    sio.emit("agents_update", public_agents, to=sid)


# forwarding command to agent

@sio.event
def execute_command(sid, data):
    target = data["target"]
    command = data["command"]

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
def command_result(sid, data):

# forwarding command results back to controller

    controller_sid = data["controller_sid"]

    sio.emit(
        "command_result",
        data,
        to=controller_sid
    ) 

#file transfer

@sio.event
def upload_file(sid, data):
   
    target = data["target"]
    
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
def upload_result(sid, data):

# Forwarding Transfer file result back to controller

    controller_sid = data.get("controller_sid")
    if controller_sid:
        sio.emit("upload_result", data, to=controller_sid)
    else:
        print(f"Warning: Received 'upload_result' from agent {sid} without a 'controller_sid'. Cannot forward.")
    
# Download file 

@sio.event
def download_file(sid, data):
    
    target = data["target"]
    filename = data.get("filename")
    
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
def download_result(sid, data):
    
    # Forwarding Download file result back to controller
    
    controller_sid = data["controller_sid"]

    sio.emit(
        "download_result",
        data,
        to=controller_sid
    )
  
    # screenshot
    
# Screenshot

@sio.event()
def screenshot(sid, data):
    
    target = data["target"]
    
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
def screenshot_result(sid, data):
    
    # Forwarding Screenshot result back to controller
    
    controller_sid = data.get("controller_sid")
    if controller_sid:
        sio.emit("screenshot_result", data, to=controller_sid)
    else:
        print(f"Warning: Received 'screenshot_result' from agent {sid} without a 'controller_sid'. Cannot forward.")


# Process management

@sio.event
def get_processes(sid, data):
    
    # Get Process list

    target = data["target"]

    target_sid = (
        agent_registry.get_sid(target)
        if agent_registry.is_agent_online(target)
        else None
    )

    sio.emit(
        "get_processes",
        {
            "controller_sid": sid
        },
        to=target_sid
    )
    
@sio.event
def process_list(sid, data):

    # Forwarding Process list back to controller

    sio.emit(
        "process_list",
        data,
        to=data["controller_sid"]
    )


@sio.event
def kill_process(sid, data):
    
    # Kill process

    target = data["target"]

    target_sid = (
        agent_registry.get_sid(target)
    )

    sio.emit(
        "kill_process",
        {
            "controller_sid": sid,
            "pid": data["pid"]
        },
        to=target_sid
    )
    
@sio.event
def kill_result(sid, data):

    # Forwarding Kill process result back to controller

    sio.emit(
        "kill_result",
        data,
        to=data["controller_sid"]
    )
    

@sio.event
def start_process(sid, data):
    
    # Start process

    target = data["target"]

    target_sid = (
        agent_registry.get_sid(target)
    )

    sio.emit(
        "start_process",
        {
            "controller_sid": sid,
            "command": data["command"]
        },
        to=target_sid
    )    

@sio.event
def start_result(sid, data):
    
    # Forwarding Start process result back to controller

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