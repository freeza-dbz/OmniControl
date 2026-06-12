import psutil
import subprocess


class ProcessManager:

    @staticmethod
    def list_processes():

        processes = []

        for proc in psutil.process_iter( ['pid', 'name'] ):

            try:

                processes.append(
                    {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"]
                    }
                )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                pass

        return processes

    @staticmethod
    def kill_process(pid):

        try:

            process = psutil.Process( int(pid) )

            process.terminate()

            return {
                "status": "success",
                "message": f"Process {pid} terminated"
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }

    @staticmethod
    def start_process(command):

        try:

            subprocess.Popen(command)

            return {
                "status": "success",
                "message": f"Started {command}"
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }