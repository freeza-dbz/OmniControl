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
    """Returns a dictionary of agents safe for public consumption."""
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
    """Handles a request from a controller to get the current agent list."""
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

# forwarding command results back to controller
 
@sio.event
def command_result(sid, data):
    controller_sid = data["controller_sid"]

    sio.emit(
        "command_result",
        data,
        to=controller_sid
    )

# server starting 

if __name__ == "__main__":
    print("----------Relay server started on port 5000----------")

    eventlet.wsgi.server(
        eventlet.listen(("0.0.0.0", 5000)),
        app
    )