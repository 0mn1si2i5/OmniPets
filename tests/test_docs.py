import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_chinese_default_readme_and_english_entry_define_the_same_public_boundary(self):
        chinese = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (ROOT / "README.en.md").read_text(encoding="utf-8")
        self.assertIn("README.en.md", chinese)
        self.assertIn("README.md", english)
        for text in (chinese, english):
            self.assertIn("OmniPets", text)
            self.assertIn("OmniPet", text)
            self.assertIn("catalog/index.json", text)
            self.assertIn("pet.json", text)
            self.assertIn("spritesheet.webp", text)
            self.assertIn("LICENSE-ASSETS", text)
            self.assertIn("omnipet release export", text)
            self.assertIn("omnipet release verify", text)
        self.assertIn("public catalog", english)
        self.assertIn("公开", chinese)
        self.assertNotIn("public production repository", english.lower())


if __name__ == "__main__":
    unittest.main()
