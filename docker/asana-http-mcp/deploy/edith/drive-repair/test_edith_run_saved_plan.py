import unittest
from types import SimpleNamespace
from edith_run_saved_plan import execute

class RunnerTests(unittest.TestCase):
    def fake(self):
        rows=[{'source_id':i,'planned_path':'dest/'+i+'.png','action':'copy'} for i in ['done','new','later']]
        done={'source_id':'done','active_id':'out-done','path':'dest/done.png','name':'done.png','md5Checksum':'abc','size':'2'}
        state={'copies':{'done':done},'archived':['done'],'folders':{'dest':'dest-id'}}
        calls=[]
        def copyrow(row):
            fid=row['source_id'];calls.append(('copy',fid))
            p=dict(done,source_id=fid,active_id='out-'+fid,path=row['planned_path'],name=fid+'.png');state['copies'][fid]=p;return p
        def archive(fid,parent):calls.append(('archive',fid));state['archived'].append(fid)
        m=SimpleNamespace(plan={'file_plan':rows},state=state,orig={r['source_id']:{'path':r['source_id']+'.png'} for r in rows},
            now=lambda:'now',copyrow=copyrow,archive=archive,folder=lambda p:'archive',persist=lambda:None,save=lambda *a:None)
        return m,calls
    def test_skips_completed_before_calls(self):
        m,calls=self.fake();r=execute(m,'exports');self.assertEqual(r['processed'],2);self.assertEqual(r['status'],'phase-complete');self.assertNotIn(('copy','done'),calls)
    def test_stops_on_uncertain_write(self):
        m,calls=self.fake()
        def fail(row):calls.append(('copy',row['source_id']));raise RuntimeError('uncertain write')
        m.copyrow=fail;r=execute(m,'exports');self.assertEqual(r['status'],'blocked');self.assertEqual(calls,[('copy','new')]);self.assertEqual(r['remaining_in_phase'],2)
    def test_phase_filter(self):
        m,calls=self.fake();r=execute(m,'photoshop');self.assertEqual(r['selected'],0);self.assertEqual(calls,[])
if __name__=='__main__':unittest.main()

