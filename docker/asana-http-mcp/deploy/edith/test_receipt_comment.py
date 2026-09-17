import unittest
from receipt_comment import post_once


class ReceiptTests(unittest.TestCase):
    def test_lost_response_and_repeated_invocation(self):
        rows = []
        def call(name, args):
            if name == 'asana_get_task_stories': return rows
            rows.append({'gid': 'story1', 'text': args['text']})
            raise TimeoutError('Response lost after server commit')
        self.assertEqual(post_once(call, 'task1', 'Saved checkpoint')['gid'], 'story1')
        self.assertEqual(post_once(call, 'task1', 'Saved checkpoint')['gid'], 'story1')
        self.assertEqual(len(rows), 1)

    def test_no_blind_retry(self):
        writes = []
        def call(name, args):
            if name == 'asana_get_task_stories': return []
            writes.append(args)
            raise TimeoutError('Unknown outcome')
        with self.assertRaisesRegex(RuntimeError, 'no automatic retry'):
            post_once(call, 'task1', 'Saved checkpoint')
        self.assertEqual(len(writes), 1)


if __name__ == '__main__': unittest.main()
