import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PullRequestScopeTests(unittest.TestCase):
    def check(self, paths, expected):
        with tempfile.NamedTemporaryFile() as value:
            value.write(b"\0".join(path.encode() for path in paths) + b"\0")
            value.flush()
            result = subprocess.run([
                sys.executable,
                str(ROOT / "scripts/verify-pr-scope.py"),
                "--paths-file",
                value.name,
            ])
        self.assertEqual(result.returncode == 0, expected)

    def test_accepts_one_pet_plus_catalog(self):
        self.check([
            "pets/sushi/release.json",
            "pets/sushi/spritesheet.webp",
            "catalog/index.json",
        ], True)

    def test_rejects_catalog_only_second_pet_and_repository_changes(self):
        for paths in (
            ["catalog/index.json"],
            ["pets/sushi/release.json", "pets/other/release.json", "catalog/index.json"],
            ["pets/sushi/release.json", "README.md", "catalog/index.json"],
            ["pets/sushi/release.json", ".github/workflows/verify.yml", "catalog/index.json"],
        ):
            with self.subTest(paths=paths):
                self.check(paths, False)


if __name__ == "__main__":
    unittest.main()

