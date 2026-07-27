import requests
import re
import os

API_BASE = "https://fill.papermc.io/v3/projects/paper"

raw_paper_versions = {}
paper_versions = []

def fetch_paper_versions():
    global raw_paper_versions
    try:
        data = requests.get(API_BASE).json()
        v = data.get("versions")
        if not v:
            return None

        raw_paper_versions = v

    except Exception:
        return None

def download_paper(version_idx: int, dest: str) -> int:
    try:
        versions = requests.get(API_BASE).json().get("versions")
        if not versions:
            return 4
    except Exception:
        return 3

    if version_idx < 0 or version_idx >= len(versions):
        return 1

    version = versions[version_idx]

    try:
        builds = requests.get(f"{API_BASE}/versions/{version}").json().get("builds")
        if not builds:
            return 4
        latest_build = builds[-1]
    except Exception:
        return 3

    download_url = (
        f"{API_BASE}/versions/{version}/builds/{latest_build}/downloads/"
        f"paper-{version}-{latest_build}.jar"
    )

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

fetch_paper_versions()

def get_paper_versions() -> list[str]:
    global raw_paper_versions

    def version_key(v: str):
        match = re.match(r"(\d+)\.(\d+)(?:\.(\d+))?", v)
        if not match:
            return (0, 0, 0)

        return (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3) or 0)
        )

    versions = []

    for branch in sorted(raw_paper_versions.keys(), key=version_key):
        versions.append(branch)
        versions.extend(sorted(raw_paper_versions[branch], key=version_key))

    versions.reverse()

    return versions

paper_versions = get_paper_versions()