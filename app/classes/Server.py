import subprocess
import uuid
import os
import threading
from pathlib import Path
import shutil
import time

class Server:
    def gen_id(self, server_list: list):

        max_id: int = 0

        for server_idx in range(len(server_list)):
            if server_list[server_idx].server_id > max_id:
                max_id = server_list[server_idx].server_id

        self.server_id = max_id + 1

    def generate_command(self):
        return f"java -Xms{self.xms} -Xmx{self.xmx} -jar {os.path.join(self.executable_full_path, self.executable)} nogui".split(" ")

    def handle_output(self):
        if self.process.stdout:
            for line in self.process.stdout:
                if self.running:
                    if self.show_output:
                        line = line.strip()
                        self.new_lines.append(line)
                else:
                    break

        self.running = False

    def get_new_log(self) -> list[str]:
        newLines = self.new_lines.copy()
        self.logs.extend(newLines)
        self.new_lines.clear()
        return newLines

    def __init__(self, name: str, description: str, version: str, software: str, max_player: int, online_players: int, gen_id: bool = True, server_list: list = [], xms: str = "1G", xmx: str = "2G", eula: bool = False, new: bool = True) -> None:
        self.name: str = name
        self.version: str = version
        self.software: str = software
        self.max_player: int = max_player
        self.server_id: int
        self.online: bool = False
        self.description = description
        self.online_players = online_players
        self.executable = "server.jar"
        self.root_dir = Path(__file__).resolve().parents[2]
        self.server_root_dir = str(uuid.uuid4())
        self.executable_full_path: str = str(self.root_dir / "servers" / self.server_root_dir)
        self.xms = xms
        self.xmx = xmx
        self.process: subprocess.Popen[str]
        self.running: bool = False
        self.logs: list[str] = []
        self.new_lines: list[str] = []
        self.handle_output_thread: threading.Thread = threading.Thread(target=self.handle_output)
        self.can_start: bool = True
        self.show_output = False

        if os.path.exists(self.executable_full_path) and os.path.isdir(self.executable_full_path):
            self.can_start = False
        else:
            os.mkdir(self.executable_full_path)
            shutil.copy(os.path.join(self.root_dir, "server.jar"), self.executable_full_path)

            with open(os.path.join(self.root_dir, "servers", self.server_root_dir, 'eula.txt'), 'w') as f:
                f.write("eula=" + str(eula).lower())

        if gen_id:
            self.gen_id(server_list)

    def stop(self) -> int:
        if self.running and self.process.stdin:
            self.running = False
            self.process.communicate("/stop")
            self.process.stdin.flush()
            time.sleep(5)
            if self.process.poll():
                return 0
            else:
                self.process.terminate()
                time.sleep(5)
                if self.process.poll():
                    return 0
                else:
                    return 1
        return 1

    def kill(self):
        if self.process.poll() is not None:
            self.process.kill()

    def start_server(self) -> int:
        if self.running or not self.can_start:
            return 1

        self.process = subprocess.Popen(self.generate_command(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.path.join(self.root_dir, "servers", self.server_root_dir))
        return 0

    def send(self, inp: str):
        if self.running and self.process.stdin is not None:
            self.process.communicate(inp + "\n")
            self.process.stdin.flush()

    def to_dict(self):
        return {
            "id": self.server_id,
            "name": self.name,
            "version": self.version,
            "software": self.software,
            "max_player": self.max_player,
            "description": self.description,
            "executable": self.executable,
            "root_dir": self.server_root_dir,
            "xms": self.xms,
            "xmx": self.xmx
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["name"],
            data["description"],
            data["version"],
            data["software"],
            data["max_player"],
            data["executable"],
            data["root_dir"],
            data["xms"],
            data["xmx"]
        )