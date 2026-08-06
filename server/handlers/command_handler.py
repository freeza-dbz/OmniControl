from shared.validator import Validator
from shared.logger import get_logger

logger = get_logger("server")

def register_command_handlers(sio, agent_registry, require_role, agent_service):
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
