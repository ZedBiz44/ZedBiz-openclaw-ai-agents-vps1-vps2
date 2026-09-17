import unittest
from sanitize_evidence import sanitize


class RedactionTests(unittest.TestCase):
    def test_synthetic_credential_formats(self):
        cases = ['Password:\n\n\nSYNTHETIC-secret-value',
                 'Authorization: Bearer SYNTHETIC-token',
                 '-----BEGIN PRIVATE KEY-----\nSYNTHETIC\n-----END PRIVATE KEY-----',
                 'AKIAABCDEFGHIJKLMNOP', 'ghp_abcdefghijklmnopqrstuvwxyz',
                 'github_pat_abcdefghijklmnop', 'sk-proj-abcdefghijklmnop',
                 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.SYNTHETICsignature',
                 'https://user:synthetic-password@example.invalid']
        for raw in cases:
            with self.subTest(raw=raw):
                clean, held = sanitize(raw)
                self.assertTrue(held)
                self.assertNotIn(raw, clean)
                self.assertNotIn('SYNTHETIC', clean)

    def test_business_text_retained(self):
        self.assertEqual(sanitize('A mountain resort campaign with five images.'),
                         ('A mountain resort campaign with five images.', False))


if __name__ == '__main__': unittest.main()
