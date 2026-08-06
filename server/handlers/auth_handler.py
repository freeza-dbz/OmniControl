import socketio
from shared.auth import AGENT_TOKEN, CONTROLLER_TOKEN
from shared.validator import Validator
from shared.logger import get_logger

logger = get_logger("server")

def register_auth_handlers(sio, agent_registry, require_role, agent_service):
    @sio.event
    def connect(sid, environ, auth=None):
        logger.info(f"Client attempting to connect: {sid}")
        token = auth.get("token") if auth else None
        
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

        public_agents = agent_service.get_public_agents()
        sio.emit("agents_update", public_agents, to=sid)

    @sio.event
    def disconnect(sid):
        logger.info(f"Client disconnected: {sid}")
        print("----------CLIENT DISCONNECTED----------", sid)
        device_to_remove = agent_registry.remove(sid)
        if device_to_remove:
            print("----------AGENT REMOVED----------", device_to_remove)
            agent_service.broadcast_agent_update()
