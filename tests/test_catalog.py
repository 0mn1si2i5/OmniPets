import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def test_empty_catalog_is_canonical_and_checkable(self):
        catalog = json.loads((ROOT / "catalog/index.json").read_text())
        self.assertEqual(catalog, {"schemaVersion": 1, "pets": []})
        subprocess.run(
            [sys.executable, "scripts/build-catalog.py", "--check"],
            cwd=ROOT,
            check=True,
        )

    def test_builder_is_deterministic_and_rejects_duplicate_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_release(root, "zeta", "Zeta", "1.0.0")
            self._write_release(root, "alpha", "Alpha", "1.2.0")
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/build-catalog.py"), "--root", str(root)],
                check=True,
            )
            first = (root / "catalog/index.json").read_bytes()
            data = json.loads(first)
            self.assertEqual([item["id"] for item in data["pets"]], ["alpha", "zeta"])
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/build-catalog.py"), "--root", str(root)],
                check=True,
            )
            self.assertEqual((root / "catalog/index.json").read_bytes(), first)

            release = json.loads((root / "pets/zeta/release.json").read_text())
            release["petId"] = "alpha"
            (root / "pets/zeta/release.json").write_text(json.dumps(release))
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build-catalog.py"), "--root", str(root)],
            )
            self.assertNotEqual(result.returncode, 0)

    def _write_release(self, root, pet_id, display_name, version):
        pet = root / "pets" / pet_id
        pet.mkdir(parents=True)
        (pet / "pet.json").write_text(json.dumps({
            "id": pet_id,
            "displayName": display_name,
            "description": "A pet.",
            "spriteVersionNumber": 2,
            "spritesheetPath": "spritesheet.webp",
        }))
        (pet / "release.json").write_text(json.dumps({
            "schemaVersion": 1,
            "petId": pet_id,
            "version": version,
            "omnipetVersion": "0.1.0a1",
            "spriteVersionNumber": 2,
            "files": {
                "pet.json": "sha256:" + "a" * 64,
                "spritesheet.webp": "sha256:" + "b" * 64,
                "preview.webp": "sha256:" + "c" * 64,
                "README.md": "sha256:" + "d" * 64,
                "LICENSE-ASSETS": "sha256:" + "e" * 64,
            },
            "license": "CC-BY-NC-4.0",
        }))


if __name__ == "__main__":
    unittest.main()

