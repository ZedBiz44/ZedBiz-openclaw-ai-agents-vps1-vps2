import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('driver', Path(__file__).with_name('amanda-host-start.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = Path(self.tmp.name)
        self.lock_patch = patch.object(d, 'RESTORE_LOCK', p/'restore.lock')
        self.lock_patch.start()
        self.addCleanup(self.lock_patch.stop)
        (p/'wrapper').write_text('approved')
        (p/'images.tar').write_bytes(b'archive')
        self.m = dict(wrapper=str(p/'wrapper'), wrapper_sha256=d.digest(p/'wrapper'),
                      archive=str(p/'images.tar'), sha256=d.digest(p/'images.tar'),
                      images=[dict(ref='current', id='sha256:good', automatic=True),
                              dict(ref='old', id='sha256:old', automatic=False)])
        self.loaded = False
        self.missing = False
        self.calls = []
        self.exits = [0]

    def run_command(self, args, **kwargs):
        self.calls.append(args)
        if 'config' in args:
            return 0, 'current\n'
        if 'info' in args:
            return 0, 'version'
        if 'inspect' in args:
            return (1, '') if self.missing and not self.loaded else (0, 'sha256:good\n')
        if 'load' in args:
            self.loaded = True
            return 0, ''
        return self.exits.pop(0), 'PRIVATE OUTPUT MUST NOT BE LOGGED'

    def test_existing_image_no_load(self):
        self.assertEqual(d.start(self.m, self.run_command), 0)
        self.assertFalse(self.loaded)

    def test_missing_image_verified_restore(self):
        self.missing = True
        self.assertEqual(d.start(self.m, self.run_command), 0)
        self.assertTrue(self.loaded)

    def test_corrupt_archive_fails_before_load(self):
        self.missing = True
        self.m['sha256'] = 'bad'
        with self.assertRaisesRegex(RuntimeError, 'checksum'):
            d.start(self.m, self.run_command)
        self.assertFalse(self.loaded)

    def test_changed_image_fails(self):
        self.m['images'][0]['id'] = 'different'
        with self.assertRaisesRegex(RuntimeError, 'identity changed'):
            d.start(self.m, self.run_command)

    def test_changed_wrapper_fails(self):
        self.m['wrapper_sha256'] = 'bad'
        with self.assertRaisesRegex(RuntimeError, 'wrapper differs'):
            d.start(self.m, self.run_command)
        self.assertEqual(self.calls, [])

    def test_retry_success(self):
        self.exits = [1, 0]
        sleeps = []
        self.assertEqual(d.start(self.m, self.run_command, sleeps.append), 0)
        self.assertEqual(sleeps, [30])

    def test_retry_exhaustion(self):
        self.exits = [1, 1, 1]
        sleeps = []
        self.assertEqual(d.start(self.m, self.run_command, sleeps.append), 1)
        self.assertEqual(sleeps, [30, 30])

    def test_uncertain_timeout_not_retried(self):
        with patch.object(d, 'recover'):
            def timeout(*args, **kwargs):
                raise RuntimeError('command timed out')
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                d.start(self.m, timeout, lambda _: self.fail('must not retry'))


if __name__ == '__main__':
    unittest.main()

