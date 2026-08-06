from shared.validator import Validator
from shared.logger import get_logger

logger = get_logger("server")

def register_screenshot_handlers(sio, agent_registry, require_role, agent_service):
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
