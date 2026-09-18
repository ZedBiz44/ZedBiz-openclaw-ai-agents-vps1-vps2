import unittest
from edith_duplicate_proof import make_proof
class DuplicateProofTests(unittest.TestCase):
    def setUp(self):
        self.row={'source_id':'duplicate','active_copy_source_id':'original','action':'copy','planned_path':'folder/n.png'}
        self.source={'id':'duplicate','name':'old.png','md5Checksum':'abc','size':'42'}
        self.active={'id':'output','name':'n.png','md5Checksum':'abc','size':'42'}
        self.proof={'source_id':'original','active_id':'output','name':'n.png','path':'folder/n.png','md5Checksum':'abc','size':'42','content_read':'observed content','permissions_matched':True}
    def make(self,**kw):
        data=dict(row=self.row,original=self.source,source=self.source,active=self.active,canonical=self.proof,source_access=['same'],active_access=['same'],now='now');data.update(kw);return make_proof(**data)
    def test_own_source_proof(self):
        p=self.make();self.assertEqual(p['source_id'],'duplicate');self.assertEqual(p['active_id'],'output')
    def test_changed_content_refused(self):
        with self.assertRaises(AssertionError):self.make(source=dict(self.source,md5Checksum='changed'))
    def test_different_access_refused(self):
        with self.assertRaises(AssertionError):self.make(active_access=['different'])
    def test_different_destination_refused(self):
        with self.assertRaises(AssertionError):self.make(row=dict(self.row,planned_path='wrong/n.png'))
if __name__=='__main__':unittest.main()

