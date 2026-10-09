import requests
import re
import os

API_BASE = "https://fill.papermc.io/v3/projects/paper"
headers = {
    "User-Agent": "breadUI/0.1 (https://github.com/zack2patate18/breadUI)"
}

raw_paper_versions = {}
paper_versions = []

def fetch_paper_versions():
    global raw_paper_versions
    try:
        data = requests.get(API_BASE, headers=headers).json()
        v = data.get("versions")
        if not v:
            return None

        raw_paper_versions = v

    except Exception:
        return None

def download_paper(version_idx: int, dest: str) -> int:
    global paper_versions

    if version_idx < 0 or version_idx >= len(paper_versions):
        return 1

    version = paper_versions[version_idx]

    try:
        builds_url = f"{API_BASE}/versions/{version}/builds"
        response = requests.get(builds_url, headers=headers, timeout=15)
        response.raise_for_status()
        builds = response.json()

        stable_builds = [
            build for build in builds
            if build.get("channel") == "STABLE"
        ]

        if not stable_builds:
            stable_builds = [
                build for build in builds
                if build.get("channel") == "BETA"
            ]

            if not stable_builds:
                stable_builds = [
                    build for build in builds
                    if build.get("channel") == "ALPHA"
                ]

        latest_build = max(stable_builds, key=lambda build: build["id"])

    except Exception:
        return 3

    download_url = latest_build["downloads"]["server:default"]["url"]

    try:
        file_data = requests.get(
            download_url,
            headers=headers,
            timeout=60
        )
        file_data.raise_for_status()

        if file_data.status_code != 200:
            return 3

    except Exception:
        return 3
    
    if os.path.isdir(dest):
        dest = str(os.path.join(dest, "server.jar"))

    try:
        with open(dest, "wb") as f:
            f.write(file_data.content)

    except Exception as e:
        print(e)
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