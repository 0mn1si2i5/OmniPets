#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SEMVER = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?")
RELEASE_KEYS = {
    "schemaVersion", "petId", "version", "omnipetVersion",
    "spriteVersionNumber", "files", "license",
}


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: Path) -> dict[str, object]:
    pets_root = root / "pets"
    entries: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for directory in sorted(pets_root.iterdir() if pets_root.is_dir() else ()):
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError("pet directory is unsafe")
        release = json.loads((directory / "release.json").read_text(encoding="utf-8"))
        manifest = json.loads((directory / "pet.json").read_text(encoding="utf-8"))
        if set(release) != RELEASE_KEYS or release.get("schemaVersion") != 1:
            raise ValueError("release record schema is invalid")
        pet_id = release.get("petId")
        version = release.get("version")
        if (
            not isinstance(pet_id, str)
            or pet_id != directory.name
            or pet_id in seen_ids
            or manifest.get("id") != pet_id
            or not isinstance(version, str)
            or SEMVER.fullmatch(version) is None
            or release.get("spriteVersionNumber") != 2
            or manifest.get("spriteVersionNumber") != 2
        ):
            raise ValueError("release identity is invalid")
        files = release.get("files")
        if not isinstance(files, dict) or not all(
            isinstance(name, str) and isinstance(digest, str)
            for name, digest in files.items()
        ):
            raise ValueError("release files are invalid")
        paths = {
            "manifest": f"pets/{pet_id}/pet.json",
            "spritesheet": f"pets/{pet_id}/spritesheet.webp",
            "preview": f"pets/{pet_id}/preview.webp",
        }
        if seen_paths.intersection(paths.values()):
            raise ValueError("catalog path is duplicated")
        seen_ids.add(pet_id)
        seen_paths.update(paths.values())
        entries.append({
            "id": pet_id,
            "displayName": manifest.get("displayName"),
            "version": version,
            "spriteVersionNumber": 2,
            "paths": paths,
            "license": release.get("license"),
            "files": dict(sorted(files.items())),
            "releaseSha256": f"sha256:{sha256(directory / 'release.json')}",
        })
    return {"schemaVersion": 1, "pets": entries}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        content = canonical(build(root))
        destination = root / "catalog/index.json"
        if args.check:
            if not destination.is_file() or destination.read_bytes() != content:
                raise ValueError("catalog is stale")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        print("catalog build failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

