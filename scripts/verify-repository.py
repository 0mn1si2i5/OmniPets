#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


DENIED_NAMES = {
    "pet.yaml", "brief.md", "checkpoint", ".omnipet", "prompts", "qa",
    "PROVENANCE.json", "BUDGET.md",
}
ABSOLUTE = re.compile(
    r"(^|[\s`\"'(=])(?:/(?!/)[^\s`\"')]+|[A-Za-z]:\\[^\r\n`\"')]+|\\\\[^\\/\s]+\\[^\s`\"')]+)"
)
CREDENTIAL = re.compile(
    r"(?i)(?:(?:^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}|"
    r"(?:[A-Za-z][A-Za-z0-9]*_)?API_?KEY\s*[:=]\s*\S+|"
    r"AUTHORIZATION\s*[:=]\s*\S+)"
)


def release_version(value: str) -> tuple[object, ...]:
    match = re.fullmatch(
        r"(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?",
        value,
    )
    if match is None:
        raise ValueError("invalid version")
    major, minor, patch, prerelease = match.groups()
    if prerelease is None:
        prerelease_key: tuple[object, ...] = (1,)
    else:
        identifiers: list[tuple[int, object]] = []
        for identifier in prerelease.split("."):
            if not identifier:
                raise ValueError("invalid version")
            if identifier.isdigit():
                if len(identifier) > 1 and identifier.startswith("0"):
                    raise ValueError("invalid version")
                identifiers.append((0, int(identifier)))
            else:
                identifiers.append((1, identifier))
        prerelease_key = (0, tuple(identifiers))
    return int(major), int(minor), int(patch), prerelease_key


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--base-ref")
    args = parser.parse_args()
    root = args.root.resolve()
    omnipet = os.environ.get("OMNIPET_BIN", "omnipet")
    try:
        for path in root.rglob("*"):
            if ".git" in path.relative_to(root).parts:
                continue
            if path.is_symlink():
                raise ValueError("repository contains a symlink")
            if path.name in DENIED_NAMES:
                raise ValueError("repository contains production material")
        pets_root = root / "pets"
        for pet in sorted(pets_root.iterdir() if pets_root.is_dir() else ()):
            release = json.loads((pet / "release.json").read_text(encoding="utf-8"))
            declared = set(release["files"])
            actual = {path.name for path in pet.iterdir() if path.is_file()}
            if actual != declared | {"release.json"}:
                raise ValueError("pet bundle contains undeclared files")
            subprocess.run(
                [omnipet, "release", "verify", str(pet)],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            if args.base_ref:
                previous = subprocess.run(
                    ["git", "show", f"{args.base_ref}:pets/{pet.name}/release.json"],
                    cwd=root,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if previous.returncode == 0:
                    old = json.loads(previous.stdout)
                    if release_version(release["version"]) < release_version(old["version"]):
                        raise ValueError("pet version regressed")
        subprocess.run(
            [sys.executable, str(root / "scripts/build-catalog.py"), "--root", str(root), "--check"],
            cwd=root,
            check=True,
        )
        for path in root.rglob("*"):
            if not path.is_file() or ".git" in path.relative_to(root).parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeError:
                continue
            lines = text.splitlines()
            if lines and lines[0].startswith("#!"):
                text = "\n".join(lines[1:])
            if ABSOLUTE.search(text) or CREDENTIAL.search(text):
                raise ValueError("repository text is not portable")
        print("public repository verification passed")
        return 0
    except (
        OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError,
        ValueError, subprocess.CalledProcessError,
    ):
        print("public repository verification failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
