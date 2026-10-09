import subprocess
import uuid
import os
import threading
from pathlib import Path
import shutil
import time
import json
from app.utils.vanilla import *
from app.utils.paper import *

class Server:
    def gen_id(self, server_list: list):

        max_id: int = 0

        for server_idx in range(len(server_list)):
            if server_list[server_idx].server_id > max_id:
                max_id = server_list[server_idx].server_id

        self.server_id = max_id + 1

    def generate_command(self):
        return f"java -Xms{self.xms} -Xmx{self.xmx} -jar {os.path.join(self.executable_full_path, self.executable)} nogui".split(" ")

    def read_stream(self, stream):
        for line in iter(stream.readline, ''):
            if line:
                self.new_lines.append(line.strip())


    def handle_output(self):
        threading.Thread(
            target=self.read_stream,
            args=(self.process.stdout,)
        ).start()

        threading.Thread(
            target=self.read_stream,
            args=(self.process.stderr,)
        ).start()

    def get_new_log(self) -> list[str]:
        newLines = self.new_lines.copy()
        self.logs.extend(newLines)
        self.new_lines.clear()
        return newLines
    
    def has_server_file(self) -> bool:
        if os.path.exists(Path(self.executable_full_path) / self.executable):
            return True
        return False
    
    def create_server_files(self) -> None:
        os.mkdir(self.executable_full_path)

        with open(os.path.join(self.root_dir, "servers", self.server_root_dir, 'eula.txt'), 'w') as f:
            f.write("eula=" + str(self.eula).lower())

        with open(os.path.join(self.root_dir, "servers", self.server_root_dir, 'breadUI_metadata.json'), 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

        with open(os.path.join(self.root_dir, "servers", self.server_root_dir, 'server.properties'), 'a') as f:
            values = self.to_dict()
            for k in values.keys():
                if k == "max_player":
                    f.write(f"max-players={values[k]}\n")
                elif k == "port":
                    f.write(f"server-port={values[k]}\n")
                elif k == "name":
                    f.write(f"motd={values[k]}\n")

    def download_server_file(self, tries=3) -> bool:
        print("downloading server")
        dest = str(Path(self.executable_full_path) / "server.jar")
        if self.software == 'paper':
            version_idx  = get_paper_versions().index(self.version)
            r = download_paper(version_idx, dest)
            if r != 0:
                print("Failed to download paper server :(")
                match r:
                    case 1:
                        print("Invalid version index")
                    case 3:
                        print("Network or API error")
                    case 4:
                        print("No builds availables")
                    case 5:
                        print("Failed to create server file")
                print("Retrying", tries - 1)
                if tries > 0:
                    return self.download_server_file(tries=tries - 1)
                else:
                    return False
            else:
                print("Downloaded server")
            if self.has_server_file():
                return True
            else:
                if tries > 0:
                    return self.download_server_file(tries=tries - 1)
                else:
                    return False
            
        elif self.software == 'vanilla':
            version_idx  = get_vanilla_versions().index(self.version)
            download_vanilla(version_idx, dest)
            if self.has_server_file():
                return True
            else:
                return self.download_server_file(tries=tries - 1)

        else:
            self.can_start = False
            print("invalid software, cant download")
            return False
        
    def __init__(self, name: str, description: str, version: str, software: str, max_player: int, port: int, gen_id: bool = True, server_list: list | None = None, xms: str = "1G", xmx: str = "2G", eula: bool = False, new: bool = True, server_uuid: str | None = None, create_files=None) -> None:
        self.name: str = name
        self.version: str = version
        self.software: str = software
        self.max_player: int = max_player
        self.server_id: int
        self.online: bool = False
        self.description = description
        self.online_players = 0
        self.executable = "server.jar"
        self.root_dir = Path(__file__).resolve().parents[2]
        self.server_uuid = server_uuid
        if self.server_uuid is None:
            self.server_uuid = str(uuid.uuid4())
        self.server_root_dir = self.server_uuid
        self.executable_full_path: str = str(self.root_dir / "servers" / self.server_root_dir)
        self.xms: str = xms
        self.xmx: str = xmx
        self.process: subprocess.Popen[str]
        self.running: bool = False
        self.logs: list[str] = []
        self.new_lines: list[str] = []
        self.handle_output_thread: threading.Thread = threading.Thread(target=self.handle_output)
        self.can_start: bool = True
        self.show_output = True
        self.port: int = port
        self.eula: bool = eula
        if create_files is None:
            self.create_files = not new
        else:
            self.create_files = create_files

        if self.software not in ['paper', 'vanilla']:
            self.can_start = False
            print("invalid software")

        if self.software == 'paper' and self.version not in get_paper_versions() or self.software == 'vanilla' and self.version not in get_vanilla_versions():
            self.can_start = False
            print("invalid version for this software: " + self.software)

        if new:
            if gen_id:
                if server_list is None:
                    server_list = []
                self.gen_id(server_list)
            if os.path.exists(self.executable_full_path) and os.path.isdir(self.executable_full_path):
                self.can_start = False
                print("server executable already exist and is a directory")
            else:
                if self.create_files:
                    self.create_server_files()
                    r = self.download_server_file()
                    if not r:
                        self.can_start = False

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
        self.handle_output_thread.start()
        self.running = True
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
            "xmx": self.xmx,
            "port": self.port
        }
    
    @classmethod
    def from_dict(cls, data):
        server = cls(
            name=data["name"],
            description=data["description"],
            version=data["version"],
            software=data["software"],
            max_player=data["max_player"],
            port=data["port"],
            xms=data["xms"],
            xmx=data["xmx"],
            gen_id=False,
            new=False,
            server_uuid=data["root_dir"]
        )

        server.server_id = data["id"]
        server.executable = data["executable"]

        return server