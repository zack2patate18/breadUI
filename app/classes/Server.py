class Server:
    def gen_id(self, server_list: list):

        max_id: int = 0

        for server_idx in server_list:
            if server_list[server_idx].server_id > max_id:
                max_id = server_list[server_idx].server_id

        self.server_id = max_id

    def __init__(self, name: str, description: str, version: str, software: str, max_player: int, online_players: int, gen_id: bool = True, server_list: list = []) -> None:
        self.name: str = name
        self.version: str = version
        self.software: str = software
        self.max_player: int = max_player
        self.server_id: int
        self.online: bool = False
        self.description = description
        self.online_players = online_players

        if gen_id:
            self.gen_id(server_list)

    def to_dict(self):
        return {
            "id": self.server_id,
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
            data["description"],
            data["version"],
            data["software"],
            data["max_player"],
            data["online_players"]
        )