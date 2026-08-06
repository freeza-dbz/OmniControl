from shared.validator import Validator
from shared.logger import get_logger

logger = get_logger("server")

def register_file_handlers(sio, agent_registry, require_role, agent_service):
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
