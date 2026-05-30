import socketio
import eventlet
import eventlet.wsgi

sio = socketio.Server(
    cors_allowed_origins="*"
)

app = socketio.WSGIApp(sio)

agents = {}


@sio.event
def connect(sid, environ):
    print("CONNECTED", sid)


@sio.event
def disconnect(sid):
    print("DISCONNECTED", sid)

    for device_id, agent_sid in list(agents.items()):
        if agent_sid == sid:
            del agents[device_id]
            print("AGENT REMOVED", device_id)


@sio.event
def register_agent(sid, data):
    device_id = data["device_id"]

    agents[device_id] = sid

    print("AGENT REGISTERED", device_id)

    sio.emit(
        "registration_success",
        {"device_id": device_id},
        to=sid
    )


@sio.event
def execute_command(sid, data):
    target = data["target"]
    command = data["command"]

    if target not in agents:
        sio.emit(
            "command_result",
            {
                "status": "error",
                "message": "Agent not found "
            },
            to=sid
        )
        return

    target_sid = agents[target]

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
    controller_sid = data["controller_sid"]

    sio.emit(
        "command_result",
        data,
        to=controller_sid
    )


if __name__ == "__main__":
    print("Relay server started on port 5000")

    eventlet.wsgi.server(
        eventlet.listen(("0.0.0.0", 5000)),
        app
    )