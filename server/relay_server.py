import socketio
import eventlet
import eventlet.wsgi

sio = socketio.Server(
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

app = socketio.WSGIApp(sio)

agents = {}

def _get_public_agents():
    """Returns a dictionary of agents safe for public consumption."""
    return {
        device_id: {
            "hostname": agent_data["hostname"],
            "username": agent_data["username"],
            "os": agent_data["os"],
        }
        for device_id, agent_data in agents.items()
    }

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

    device_to_remove = None
    for device_id, agent_info in agents.items():
        if agent_info["sid"] == sid:
            device_to_remove = device_id
            break

    if device_to_remove:
        del agents[device_to_remove]
        print("----------AGENT REMOVED----------", device_to_remove)
        broadcast_agent_update()

# agent registeration

@sio.event
def register_agent(sid, data):
    device_id = data["device_id"]
    agents[device_id] = {
        "sid": sid,
        "hostname": data["hostname"],
        "username": data["username"],
        "os": data["os"]
    }

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

    if target not in agents:
        sio.emit(
            "command_result",
            {
                "status": "error",
                "message": "Agent not found"
            },
            to=sid
        )
        return

    target_sid = agents[target]["sid"]

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