from shared.logger import get_logger

logger = get_logger("server")

def register_heartbeat_handlers(sio, agent_registry, require_role, agent_service):
    @sio.event
    @require_role("agent")
    def heartbeat(sid, data):
        device_id = data.get("device_id")
        if device_id:
            agent_registry.update_last_seen(device_id)
