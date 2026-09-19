import unittest,tempfile
from pathlib import Path
from drive_copy_identity import execute,path_for

class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        self.args=['copy','source','new.png','--parent','parent'];self.calls=[];self.exists=False;self.copies=0
        self.source=dict(id='source',name='old.png',mimeType='image/png',md5Checksum='abc',size='3',driveId='drive',parents=['original'],modifiedTime='time')
        self.output=dict(self.source,id='reserved',name='new.png',parents=['parent'])
    def tearDown(self):self.tmp.cleanup()
    def raw(self,*args):
        self.calls.append(args)
        if args[0]=='generate-id':return {'id':'reserved'}
        if args[0]=='get':
            if args[1]=='source':return {'file':dict(self.source)}
            if not self.exists:raise RuntimeError('404 File not found')
            return {'file':dict(self.output)}
        self.assertEqual(args,('copy','source','new.png','--destination-id','reserved','--parent','parent'))
        self.assertTrue(path_for(self.p,self.args).exists())
        self.copies+=1
        if self.copies==1:raise RuntimeError('timeout awaiting response headers')
        self.exists=True;return {'file':{'id':'reserved'}}
    def test_timeout_retries_same_id_only(self):
        self.assertEqual(execute(self.p,self.args,self.raw,sleep=lambda _:None)['file']['id'],'reserved')
        self.assertEqual(self.copies,2);self.assertEqual(sum(c[0]=='generate-id' for c in self.calls),1)
    def test_completed_lookup_never_recopies(self):
        execute(self.p,self.args,self.raw,sleep=lambda _:None)
        execute(self.p,self.args,self.raw,sleep=lambda _:None);self.assertEqual(self.copies,2)
    def test_changed_source_is_held(self):
        execute(self.p,self.args,self.raw,sleep=lambda _:None);self.source['md5Checksum']='changed'
        with self.assertRaises(ValueError):execute(self.p,self.args,self.raw,sleep=lambda _:None)
        self.assertEqual(self.copies,2)
    def test_wrong_output_is_held(self):
        self.output['parents']=['wrong']
        with self.assertRaises(ValueError):execute(self.p,self.args,self.raw,sleep=lambda _:None)
    def test_success_lost_response_reconciles_without_retry(self):
        def raw(*args):
            if args[0]=='copy':self.exists=True;self.copies+=1;raise RuntimeError('timeout')
            return self.raw(*args)
        execute(self.p,self.args,raw,sleep=lambda _:None);self.assertEqual(self.copies,1)
    def test_permission_failure_is_not_retried(self):
        def raw(*args):
            if args[0]=='copy':self.copies+=1;raise RuntimeError('403 permission denied')
            return self.raw(*args)
        with self.assertRaises(RuntimeError):execute(self.p,self.args,raw,sleep=lambda _:None)
        self.assertEqual(self.copies,1)

if __name__=='__main__':unittest.main()

