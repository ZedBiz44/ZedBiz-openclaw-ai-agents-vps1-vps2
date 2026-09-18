import unittest
from edith_drive_recovery import candidate, reconcile

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.source = {'id':'source','md5Checksum':'abc','size':'123','driveId':'drive'}
        self.item = dict(self.source,id='copy',name='planned.png',parents=['folder'],createdTime='2026-09-18T00:00:01Z')
        self.args = ('copy','source','planned.png','--parent','folder')
        self.started = '2026-09-18T00:00:00Z'
    def test_exact_match(self):
        self.assertEqual(candidate(self.source,[self.item],self.args,self.started)['id'],'copy')
    def test_refuse_ambiguous_or_changed(self):
        for files in [[],[self.item,self.item],[dict(self.item,md5Checksum='different')],
                      [dict(self.item,parents=['elsewhere'])],[dict(self.item,createdTime='2026-09-17T00:00:00Z')]]:
            self.assertIsNone(candidate(self.source,files,self.args,self.started))
    def test_no_checksum_is_not_proof(self):
        self.assertIsNone(candidate(dict(self.source,md5Checksum=None),[self.item],self.args,self.started))
    def test_paginated_recovery_reads_only(self):
        calls=[]
        def read(*args):
            calls.append(args)
            if args[0]=='get':return {'file':self.source if args[1]=='source' else self.item}
            if '--page' in args:return {'files':[self.item]}
            return {'files':[], 'nextPageToken':'second'}
        self.assertEqual(reconcile(self.args,self.started,read)['file']['id'],'copy')
        self.assertTrue(all(a[0] in ('get','ls') for a in calls))
    def test_missing_copy_never_retries_write(self):
        calls=[]
        def read(*args):
            calls.append(args)
            return {'file':self.source} if args[0]=='get' else {'files':[]}
        self.assertIsNone(reconcile(self.args,self.started,read,sleep=lambda _:None))
        self.assertEqual(sum(a[0]=='ls' for a in calls),3)

if __name__=='__main__':unittest.main()

