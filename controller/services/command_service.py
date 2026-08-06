class CommandService:
    @staticmethod
    def execute_command(sio, target, command):
        sio.emit("execute_command", {"target": target, "command": command})
