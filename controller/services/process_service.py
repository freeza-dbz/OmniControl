import time

class ProcessService:
    @staticmethod
    def request_processes(sio, target):
        time.sleep(0.5)
        sio.emit("get_processes", {"target": target})
        
    @staticmethod
    def kill_remote_process(sio, target, pid):
        sio.emit("kill_process", {"target": target, "pid": pid})

    @staticmethod
    def start_remote_process(sio, target, command):
        sio.emit("start_process", {"target": target, "command": command})
