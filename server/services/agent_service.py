from shared.logger import get_logger

logger = get_logger("server")

class AgentService:
    def __init__(self, sio, agent_registry):
        self.sio = sio
        self.agent_registry = agent_registry

    def get_public_agents(self):
        return self.agent_registry.get_public_list()

    def broadcast_agent_update(self):
        print("--------Broadcasting the current list of agents to all clients.------")
        public_agents = self.get_public_agents()
        self.sio.emit("agents_update", public_agents)
