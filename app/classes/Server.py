class Server:
    def gen_id(self, server_list: list):
        final_id: int | None = None
        for i in range(len(server_list)):
            for j in range(len(server_list)):
                if server_list[j]["id"] == i:
                    break

            else:
                final_id = i
                self.id = final_id
                break

    def __init__(self, name: str, version: str, software: str, max_player: int, gen_id: bool = True) -> None:
        self.name: str = name
        self.version: str = version
        self.software: str = software
        self.max_player: int = max_player
        self.id: int
        self.online: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "software": self.software,
            "max_player": self.max_player
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["name"],
            data["version"],
            data["software"],
            data["max_player"]
        )