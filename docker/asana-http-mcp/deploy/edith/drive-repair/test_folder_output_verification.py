import unittest
from folder_output_verification import verify_output

class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.source = dict(name='original.png', mimeType='image/png', size='10', md5Checksum='abc')
        self.dest = dict(self.source, name='named.png')
    def check(self):
        return verify_output(None, {}, self.source, self.dest, None)
    def test_exact_binary_needs_no_download(self):
        self.assertIn('No additional download', self.check()[0])
    def test_changed_bytes_rejected(self):
        self.dest['md5Checksum']='different'
        with self.assertRaises(ValueError): self.check()
    def test_missing_hashes_never_equal(self):
        self.source.pop('md5Checksum'); self.dest.pop('md5Checksum')
        with self.assertRaises(ValueError): self.check()
    def test_extension_changes_rejected(self):
        self.dest['name']='named.jpg'
        with self.assertRaises(ValueError): self.check()
    def test_photoshop_name_preserved(self):
        self.source['name']='old.psd'; self.dest['name']='new.psd'
        with self.assertRaises(ValueError): self.check()
        self.dest['name']='old.psd'; self.check()
    def test_size_changes_rejected(self):
        self.dest['size']='11'
        with self.assertRaises(ValueError): self.check()

if __name__=='__main__': unittest.main()

