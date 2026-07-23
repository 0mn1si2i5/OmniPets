import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_repository",
    ROOT / "scripts/verify-repository.py",
)
assert SPEC is not None and SPEC.loader is not None
VERIFY_REPOSITORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY_REPOSITORY)


class RepositoryVerificationTests(unittest.TestCase):
    def test_release_version_detects_regressions_including_prereleases(self):
        parse = VERIFY_REPOSITORY.release_version
        self.assertLess(parse("0.9.0"), parse("1.0.0"))
        self.assertLess(parse("1.0.0-rc.1"), parse("1.0.0"))
        self.assertGreater(parse("1.0.1"), parse("1.0.0"))

    def test_ci_passes_pull_request_base_to_repository_verifier(self):
        workflow = (ROOT / ".github/workflows/verify.yml").read_text()
        self.assertIn('--base-ref "$BASE_REF"', workflow)
        self.assertIn("github.event.pull_request.base.sha", workflow)


if __name__ == "__main__":
    unittest.main()
