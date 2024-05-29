# Brian Lesko
# 5/28/2024
# Clear certain port processes running on the host given a list of ports

import subprocess
class PortKiller:
    def __init__(self, ports):
        self.ports = ports

    def kill_processes(self):
        for port in self.ports:
            try:
                # Find the process ID (PID) using lsof
                lsof_command = f"lsof -i :{port}"
                output = subprocess.check_output(lsof_command, shell=True).decode("utf-8").strip().split("\n")

                if len(output) > 1:
                    # Skip the first line (it's just headers)
                    for line in output[1:]:
                        pid = line.split()[1]

                        # Kill the process
                        kill_command = f"kill -9 {pid}"
                        subprocess.run(kill_command, shell=True)
                else:
                    print(f"No process found on port {port}.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to find process on port {port} with error: {e}")