import requests
import re
import os

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

raw_vanilla_versions = []
vanilla_versions = []


def fetch_vanilla_versions():
    global raw_vanilla_versions

    try:
        data = requests.get(MANIFEST_URL).json()
        raw_vanilla_versions = data.get("versions", [])
    except Exception:
        return None


def download_vanilla(version_idx: int, dest: str) -> int:
    global vanilla_versions

    if version_idx < 0 or version_idx >= len(vanilla_versions):
        return 1

    version = vanilla_versions[version_idx]

    try:
        manifest = requests.get(MANIFEST_URL).json()
        version_data = next(v for v in manifest["versions"] if v["id"] == version)
    except Exception:
        return 3

    try:
        version_json = requests.get(version_data["url"]).json()
        server = version_json["downloads"].get("server")

        if server is None:
            return 4

        download_url = server["url"]
    except Exception:
        return 3

    try:
        file_data = requests.get(download_url)
        if file_data.status_code != 200:
            return 3
    except Exception:
        return 3

    filename = os.path.join(dest, "server.jar")

    try:
        with open(filename, "wb") as f:
            f.write(file_data.content)
    except Exception:
        return 5

    return 0


fetch_vanilla_versions()


def get_vanilla_versions() -> list[str]:
    global raw_vanilla_versions

    def version_key(v: str):
        match = re.match(r"(\d+)\.(\d+)(?:\.(\d+))?", v)
        if not match:
            return (0, 0, 0)

        return (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3) or 0)
        )

    release_versions = [
        v["id"]
        for v in raw_vanilla_versions
        if v["type"] == "release"
    ]

    release_versions.sort(key=version_key, reverse=True)

    return release_versions


vanilla_versions = get_vanilla_versions()