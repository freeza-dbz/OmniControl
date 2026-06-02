class AgentRegistry:
    """Manages the collection of connected agents."""

    def __init__(self):
        self.agents = {}

    def register(self, sid: str, data: dict):
        """Registers or updates an agent's information."""
        device_id = data["device_id"]
        self.agents[device_id] = {
            "sid": sid,
            "hostname": data["hostname"],
            "username": data["username"],
            "os": data["os"]
        }
        return device_id

    def remove(self, sid: str) -> str | None:
        """Removes an agent by its SID and returns its device_id."""
        device_to_remove = None
        for device_id, agent_info in self.agents.items():
            if agent_info["sid"] == sid:
                device_to_remove = device_id
                break
        
        if device_to_remove:
            del self.agents[device_to_remove]
            return device_to_remove
        return None

    def get_public_list(self) -> dict:
        """Returns a dictionary of agents safe for public consumption."""
        return {
            device_id: {
                "hostname": agent_data["hostname"],
                "username": agent_data["username"],
                "os": agent_data["os"],
            }
            for device_id, agent_data in self.agents.items()
        }

    def get_sid(self, device_id: str) -> str | None:
        """Returns the SID for a given device_id."""
        agent = self.agents.get(device_id)
        return agent["sid"] if agent else None

    def is_agent_online(self, device_id: str) -> bool:
        """Checks if an agent with the given device_id is connected."""
        return device_id in self.agents