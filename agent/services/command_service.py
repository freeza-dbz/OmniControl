import subprocess
from shared.logger import get_logger

logger = get_logger("agent")

class CommandService:
    @staticmethod
    def run_command(command: str):
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return {"status": "success", "output": output}
        except Exception as e:
            return {"status": "error", "output": str(e)}
