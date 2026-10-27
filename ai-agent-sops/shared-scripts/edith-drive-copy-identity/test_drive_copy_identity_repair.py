import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE=Path(__file__).parent
SPEC=importlib.util.spec_from_file_location('drive_copy_identity_patched',HERE/'drive_copy_identity.py')
mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(mod)

SOURCE={'id':'source','name':'original.bin','mimeType':'application/octet-stream',
        'parents':['source-parent'],'driveId':'source-drive','md5Checksum':'abc',
        'size':'12','modifiedTime':'2026-10-26T00:00:00Z','trashed':False}
PARENT={'id':'target-parent','name':'approved','mimeType':mod.FOLDER,'parents':['root'],
        'driveId':'shared-destination','trashed':False}
ARGS=['copy','source','copy.bin','--parent','target-parent']

class MemoryRaw:
    def __init__(self,source=None,parent=None,copy_mode='create'):
        self.files={'source':dict(source or SOURCE),'target-parent':dict(parent or PARENT)}
        self.calls=[];self.generated=[];self.copy_ids=[];self.copy_mode=copy_mode
    def __call__(self,*args):
        self.calls.append(args)
        if args[0]=='get':
            if args[1] not in self.files:raise RuntimeError('404 File not found')
            return {'file':dict(self.files[args[1]])}
        if args[0]=='generate-id':
            value='reserved-%d'%(len(self.generated)+1);self.generated.append(value);return {'id':value}
        if args[0]=='copy':
            if '--destination-id' not in args:return {'file':{'id':'native-result'}}
            destination=args[args.index('--destination-id')+1];self.copy_ids.append(destination)
            if self.copy_mode=='create':
                item=dict(self.files['source'])
                item.update({'id':destination,'name':args[2],'parents':[args[-1]],
                             'driveId':self.files[args[-1]].get('driveId'),'trashed':False})
                self.files[destination]=item
            return {'file':{'id':destination}}
        raise AssertionError(args)

def local_guard():
    def save(path,record):
        Path(path).write_text(json.dumps(record))
    return types.SimpleNamespace(save=save)

class RepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_guard=sys.modules.get('execution_guard')
        sys.modules['execution_guard']=local_guard()
    def tearDown(self):
        if self.old_guard is None:sys.modules.pop('execution_guard',None)
        else:sys.modules['execution_guard']=self.old_guard
        self.tmp.cleanup()
    def run_copy(self,raw):
        return mod.execute(self.tmp.name,ARGS,raw,sleep=lambda _:None)
    def record(self,**changes):
        r={'version':1,'args':ARGS,'destination_id':'reserved-1','source':dict(SOURCE),
           'destination':{k:PARENT.get(k) for k in ['id','mimeType','driveId','trashed']},'attempts':0}
        r.update(changes);return r
    def write_record(self,record):
        p=mod.path_for(self.tmp.name,ARGS);p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(record))
    def copied(self,**changes):
        f=dict(SOURCE);f.update({'id':'reserved-1','name':'copy.bin','parents':['target-parent'],
                                  'driveId':'shared-destination','trashed':False});f.update(changes);return f
    def test_cross_shared_destination_passes_and_verify_rejects_mismatches(self):
        raw=MemoryRaw()
        answer=self.run_copy(raw)
        self.assertEqual(answer['reserved_destination_id'],'reserved-1')
        self.assertEqual(answer['file']['driveId'],'shared-destination')
        self.assertEqual(json.loads(mod.path_for(self.tmp.name,ARGS).read_text())['destination']['driveId'],'shared-destination')
        bads=[{'driveId':'wrong-drive'},{'parents':['wrong-parent']},{'name':'wrong-name'},
              {'id':'wrong-id'},{'md5Checksum':'wrong'},{'size':'13'},
              {'mimeType':'application/other'},{'trashed':True}]
        record=self.record()
        for change in bads:
            with self.subTest(change=change),self.assertRaises(ValueError):mod.verify(record,self.copied(**change))
    def test_invalid_target_folder_stops_before_reservation_or_copy(self):
        raw=MemoryRaw(parent=dict(PARENT,mimeType='text/plain'))
        with self.assertRaisesRegex(ValueError,'Approved destination parent mismatch'):self.run_copy(raw)
        self.assertEqual(raw.generated,[])
        self.assertFalse(raw.copy_ids)
    def test_uncertain_and_repeated_execution_reuses_one_reserved_id(self):
        raw=MemoryRaw(copy_mode='uncertain')
        for _ in range(2):
            with self.assertRaisesRegex(RuntimeError,'do not generate another'):self.run_copy(raw)
        self.assertEqual(raw.generated,['reserved-1'])
        self.assertEqual(set(raw.copy_ids),{'reserved-1'})
        self.assertEqual(len(raw.copy_ids),4)
    def test_source_change_after_reservation_rejects(self):
        raw=MemoryRaw();self.run_copy(raw)
        raw.files['source']['md5Checksum']='changed'
        with self.assertRaisesRegex(ValueError,'Source changed'):self.run_copy(raw)
        self.assertEqual(raw.generated,['reserved-1'])
    def test_existing_destination_authority_change_rejects(self):
        self.write_record(self.record())
        raw=MemoryRaw(parent=dict(PARENT,driveId='other-destination'))
        with self.assertRaisesRegex(ValueError,'authority changed'):self.run_copy(raw)
        self.assertEqual(raw.generated,[])
        self.assertFalse(raw.copy_ids)
    def test_legacy_same_drive_fallback_passes_but_cross_drive_rejects(self):
        legacy=self.record();legacy.pop('destination');legacy['source']['driveId']='same-drive'
        legacy_raw=MemoryRaw(source=legacy['source'],parent=dict(PARENT,driveId='same-drive'))
        legacy_raw.files['reserved-1']=self.copied(driveId='same-drive')
        self.write_record(legacy)
        self.assertEqual(self.run_copy(legacy_raw)['reserved_destination_id'],'reserved-1')
        self.assertNotIn('destination',json.loads(mod.path_for(self.tmp.name,ARGS).read_text()))
        cross=MemoryRaw(source=legacy['source'],parent=PARENT)
        with self.assertRaisesRegex(ValueError,'cannot adopt a cross-drive'):self.run_copy(cross)
    def test_native_branch_remains_raw_without_parent_preflight(self):
        native=dict(SOURCE,mimeType='application/vnd.google-apps.document',md5Checksum=None)
        raw=MemoryRaw(source=native)
        result=self.run_copy(raw)
        self.assertEqual(result,{'file':{'id':'native-result'}})
        self.assertEqual(raw.calls[0],('get','source','--fields',mod.FIELDS))
        self.assertEqual(raw.calls[1],tuple(ARGS))
        self.assertEqual(len(raw.calls),2)
        self.assertEqual(raw.generated,[])

if __name__=='__main__':
    unittest.main(verbosity=2)
