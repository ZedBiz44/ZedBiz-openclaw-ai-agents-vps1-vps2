import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("workshop_change.py")
SPEC = importlib.util.spec_from_file_location("workshop_change", MODULE_PATH)
workshop_change = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workshop_change)

READER_PATH = Path(__file__).with_name("remote_reader.py")
READER_SPEC = importlib.util.spec_from_file_location("remote_reader", READER_PATH)
remote_reader = importlib.util.module_from_spec(READER_SPEC)
READER_SPEC.loader.exec_module(remote_reader)

CONFIGURE_PATH = Path(__file__).with_name("configure_model_fallbacks.py")
CONFIGURE_SPEC = importlib.util.spec_from_file_location("configure_model_fallbacks", CONFIGURE_PATH)
configure_model_fallbacks = importlib.util.module_from_spec(CONFIGURE_SPEC)
CONFIGURE_SPEC.loader.exec_module(configure_model_fallbacks)


class WorkshopChangeTests(unittest.TestCase):
    def test_added_changed_and_deleted(self):
        before = [
            {"path": "keep/SKILL.md", "sha256": "same"},
            {"path": "change/SKILL.md", "sha256": "old"},
            {"path": "delete/SKILL.md", "sha256": "gone"},
        ]
        after = [
            {"path": "keep/SKILL.md", "sha256": "same"},
            {"path": "change/SKILL.md", "sha256": "new"},
            {"path": "add/SKILL.md", "sha256": "new"},
        ]
        self.assertEqual(workshop_change.changed_paths(before, after), {
            "added": ["add/SKILL.md"],
            "changed": ["change/SKILL.md"],
            "deleted": ["delete/SKILL.md"],
        })

    def test_reader_stays_inside_allowed_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "skills"
            root.mkdir()
            (root / "SKILL.md").write_text("safe", encoding="utf-8")
            self.assertEqual(remote_reader.safe_file(root, "SKILL.md").read_text(), "safe")
            with self.assertRaises(ValueError):
                remote_reader.safe_file(root, "../outside.txt")

    def test_workspace_index_reads_frontmatter(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / "z-test"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: z-test\ndescription: Test description\n---\n", encoding="utf-8"
            )
            self.assertEqual(remote_reader.workspace_index(root), [{
                "path": "z-test/SKILL.md",
                "name": "z-test",
                "description": "Test description",
            }])

    def test_fallback_repair_preserves_primary(self):
        data = {
            "agents": {"defaults": {
                "model": {
                    "primary": "openai/gpt-5.6-sol",
                    "fallbacks": ["openrouter/google/gemini-3.1-flash-lite", "openrouter/deepseek/deepseek-v4-flash:free"],
                },
                "models": {},
            }}
        }
        configure_model_fallbacks.configure(data)
        self.assertEqual(data["agents"]["defaults"]["model"]["primary"], "openai/gpt-5.6-sol")
        self.assertEqual(data["agents"]["defaults"]["model"]["fallbacks"][-1], "openrouter/deepseek/deepseek-v4-flash")
        self.assertEqual(data["agents"]["defaults"]["models"]["openrouter/deepseek/deepseek-v4-flash"]["params"]["maxTokens"], 8192)


if __name__ == "__main__":
    unittest.main()
