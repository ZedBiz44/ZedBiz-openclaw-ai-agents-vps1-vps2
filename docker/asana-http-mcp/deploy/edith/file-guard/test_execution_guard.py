import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from execution_guard import gate, run, digest


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.evidence = self.base / 'file-preview.txt'
        self.evidence.write_text('Synthetic own-file content observation')
        self.plan = {'file_plan': [{'source_id': 'source', 'action': 'copy', 'planned_path': 'Content/file.txt'}]}
        self.before = {'complete': True, 'items': [{'id': 'source', 'size': '10', 'md5Checksum': 'abc', 'parents': ['root']}]}
        self.write('prewrite-plan.json', self.plan)
        self.write('initial-inventory.json', self.before)
        self.review = {'plan_sha256': digest(self.base/'prewrite-plan.json'),
                       'inventory_sha256': digest(self.base/'initial-inventory.json'),
                       'reviewer': 'Edith', 'reviewed_at': '2026-09-17T20:00:00Z',
                       'representative_content_checked': True, 'archive_paths': ['Archive'], 'pilot_source_ids': ['source'],
                       'evidence': {'source': {'source_id': 'source', 'path': str(self.evidence), 'sha256': digest(self.evidence)}}}
        self.write('plan-review.json', self.review)
        self.state = {'folders': {'Content': 'dest', 'Archive': 'archive'}, 'copies': {}}
        self.write('execution-state.json', self.state)
        self.args = ('copy', 'source', 'file.txt', '--parent', 'dest')
        self.check = lambda p, b: []

    def write(self, name, x):
        (self.base/name).write_text(json.dumps(x))

    def accept(self, args=None):
        return gate(self.base, 'root', args or self.args, self.check)

    def test_exact_saved_decision(self):
        self.accept()

    def test_unplanned_name_source_parent(self):
        for args in [('copy', 'source', 'invented.txt', '--parent', 'dest'),
                     ('copy', 'unknown', 'file.txt', '--parent', 'dest'),
                     ('copy', 'source', 'file.txt', '--parent', 'wrong')]:
            with self.subTest(args=args), self.assertRaises(ValueError): self.accept(args)

    def test_changed_plan(self):
        self.plan['file_plan'][0]['planned_path'] = 'Content/new.txt'
        self.write('prewrite-plan.json', self.plan)
        with self.assertRaises(ValueError): self.accept()

    def test_changed_evidence(self):
        self.evidence.write_text('changed')
        with self.assertRaises(ValueError): self.accept()

    def test_empty_pilot_rejected(self):
        self.review['pilot_source_ids'] = []
        self.write('plan-review.json', self.review)
        with self.assertRaises(ValueError): self.accept()

    def test_missing_evidence(self):
        self.evidence.unlink()
        with self.assertRaises(ValueError): self.accept()

    def test_failed_content_gate(self):
        self.check = lambda p,b: [{'type': 'content_not_inspected'}]
        with self.assertRaises(ValueError): self.accept()

    def test_mkdir_only_reviewed_paths(self):
        self.accept(('mkdir', 'Content', '--parent', 'root'))
        with self.assertRaises(ValueError): self.accept(('mkdir', 'Invented', '--parent', 'root'))

    def test_archive_requires_verified_copy(self):
        with self.assertRaises(ValueError): self.accept(('move', 'source', '--parent', 'archive'))
        self.state['copies']['source'] = {'active_id': 'copy', 'permissions_matched': True, 'content_read': 'Opened own copy', 'size': '10', 'md5Checksum': 'abc'}
        self.write('execution-state.json', self.state)
        self.accept(('move', 'source', '--parent', 'archive'))

    def test_protected(self):
        with self.assertRaises(ValueError): self.accept(('copy', '1d6ADvC5OVsNQ_I50K944htnQP1dj7StP', 'file.txt', '--parent', 'dest'))

    def test_duplicate_confirmed_write_returns_saved_result(self):
        calls = []
        def execute():
            calls.append(1)
            return {'file': {'id': 'one-copy'}}
        for _ in range(2):
            self.assertEqual(run(self.base, 'root', self.args, execute, self.check)['file']['id'], 'one-copy')
        self.assertEqual(len(calls), 1)

    def test_lost_response_never_repeats_remote_write(self):
        calls = []
        def execute():
            calls.append('remote copy happened')
            raise TimeoutError('response lost')
        with self.assertRaises(TimeoutError): run(self.base, 'root', self.args, execute, self.check)
        with self.assertRaises(RuntimeError): run(self.base, 'root', self.args, execute, self.check)
        self.assertEqual(len(calls), 1)

    def test_interruption_never_repeats_remote_write(self):
        def execute(): raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): run(self.base, 'root', self.args, execute, self.check)
        with self.assertRaises(RuntimeError): run(self.base, 'root', self.args, execute, self.check)

    def test_destructive_command_denied(self):
        with self.assertRaises(ValueError): run(self.base, 'root', ('delete', 'source'), lambda: self.fail(), self.check)


if __name__ == '__main__': unittest.main()
