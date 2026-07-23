#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-file", required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = args.paths_file.read_bytes()
        paths = [PurePosixPath(value.decode()) for value in raw.split(b"\0") if value]
        pet_ids = {
            path.parts[1]
            for path in paths
            if len(path.parts) >= 3 and path.parts[0] == "pets"
        }
        allowed = {"catalog/index.json"}
        if len(pet_ids) != 1:
            raise ValueError("asset change must target exactly one pet")
        pet_id = next(iter(pet_ids))
        allowed_prefix = ("pets", pet_id)
        if PurePosixPath("catalog/index.json") not in paths:
            raise ValueError("catalog update is required")
        if any(
            path.as_posix() not in allowed
            and path.parts[:2] != allowed_prefix
            for path in paths
        ):
            raise ValueError("asset change exceeds one pet")
        return 0
    except (OSError, UnicodeError, ValueError):
        print("pull request scope is invalid", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

