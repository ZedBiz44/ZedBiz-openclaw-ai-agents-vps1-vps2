import importlib.util
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("patcher", pathlib.Path(__file__).with_name("patch-imap-notification-framing.py"))
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)


class FramingTests(unittest.TestCase):
    def test_only_renderer_directive_changes(self):
        prefix = b'senderAuth.min=verified; allowedSenders; pendingUids;\n'
        suffix = b'\nexternalContentSource: "email"; idempotencyKey: sessionKey;'
        original = prefix + patcher.OLD + suffix
        self.assertEqual(patcher.patch(original), prefix + patcher.NEW + suffix)

    def test_repeat_is_noop(self):
        fixed = patcher.patch(patcher.OLD)
        self.assertEqual(patcher.patch(fixed), fixed)

    def test_unknown_or_duplicate_fails_closed(self):
        for data in [b'unknown', patcher.OLD * 2, patcher.OLD + patcher.NEW]:
            with self.assertRaises(ValueError):
                patcher.patch(data)


if __name__ == '__main__':
    unittest.main()

