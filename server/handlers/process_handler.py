from shared.validator import Validator
from shared.logger import get_logger

logger = get_logger("server")

def register_process_handlers(sio, agent_registry, require_role, agent_service):
    @sio.event
    @require_role("controller")
    def get_processes(sid, data):
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
