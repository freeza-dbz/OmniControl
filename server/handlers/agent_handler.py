from shared.validator import Validator
from shared.logger import get_logger

logger = get_logger("server")

def register_agent_handlers(sio, agent_registry, require_role, agent_service):
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
        agent_service.broadcast_agent_update()

    @sio.event
    @require_role("controller")
    def get_agents(sid):
        # Handles a request from a controller to get the current agent list.
        logger.info(f"Client {sid} requested agent list.")
        print(f"----------Client {sid} requested agent list.----------")
        public_agents = agent_service.get_public_agents()
        sio.emit("agents_update", public_agents, to=sid)
