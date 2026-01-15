#!/usr/bin/env python3
# Generates build info and injects it into the server zip files.

import codecs
import hashlib
import io
import json
import os
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

FILE = "SS14.Client.zip"

SERVER_FILES = [
    "SS14.Server_linux-x64.zip",
    "SS14.Server_win-x64.zip"
]

VERSION = os.environ["GITHUB_SHA"]
print("Build version:", VERSION)

FORK_ID = "dh_test"

BUILD_URL = "http://dark-haven.xyz:8080/builds/{FORK_VERSION}/SS14.Client.zip"
MANIFEST_URL = "http://dark-haven.xyz:8080/version/{FORK_VERSION}/manifest"
MANIFEST_DOWNLOAD_URL = "http://dark-haven.xyz:8080/version/{FORK_VERSION}/download"


def main() -> None:
    client_file = os.path.join("release", FILE)
    manifest = generate_build_json(client_file)

    for server in SERVER_FILES:
        inject_manifest(os.path.join("release", server), manifest)


def inject_manifest(zip_path: str, manifest: str) -> None:
    with ZipFile(zip_path, "a", compression=ZIP_DEFLATED) as z:
        z.writestr("build.json", manifest)
        print(f"Injected build.json into {zip_path}")


def generate_build_json(file: str) -> str:
    return json.dumps({
        "download": BUILD_URL,
        "hash": sha256_file(file),
        "version": VERSION,
        "fork_id": FORK_ID,
        "engine_version": get_engine_version(),
        "manifest_url": MANIFEST_URL,
        "manifest_download_url": MANIFEST_DOWNLOAD_URL,
        "manifest_hash": generate_manifest_hash(file)
    })


def generate_manifest_hash(file: str) -> str:
    zipf = ZipFile(file)
    infos = sorted(zipf.infolist(), key=lambda i: i.filename)

    buffer = io.BytesIO()
    writer = codecs.getwriter("UTF-8")(buffer)
    writer.write("Robust Content Manifest 1\n")

    for info in infos:
        if info.filename.endswith("/"):
            continue
        data = zipf.read(info)
        h = hashlib.blake2b(data, digest_size=32).hexdigest().upper()
        writer.write(f"{h} {info.filename}\n")

    return hashlib.blake2b(buffer.getbuffer(), digest_size=32).hexdigest().upper()


def get_engine_version() -> str:
    proc = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        stdout=subprocess.PIPE,
        cwd="RobustToolbox",
        check=True,
        encoding="UTF-8"
    )
    tag = proc.stdout.strip()
    assert tag.startswith("v")
    return tag[1:]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(4096), b""):
            h.update(b)
    return h.hexdigest()


if __name__ == "__main__":
    main()
