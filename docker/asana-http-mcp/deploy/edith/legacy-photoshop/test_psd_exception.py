import sys,copy,unittest
sys.path.insert(0,'/home/node/.openclaw/workspace/skills/z-files-folders/scripts')
import check_completion as c
class Tests(unittest.TestCase):
 def setUp(self):
  self.source=dict(id='source',name='01.psd',mimeType='image/x-photoshop',md5Checksum='abc',size='5',active=True)
  self.row=dict(source_id='source',preservation_exception=c.PHOTOSHOP_POLICY,inspected=False,planned_path='ZVIM-LAF-Photoshop-Source-Files/01.psd',inspection_method='metadata-only: user-approved Photoshop preservation',inspection_evidence='metadata receipt and Jack policy',purpose='Retain legacy Photoshop source',classification_reason='Jack requested preservation without content review',active_id='copy',match_method='binary',match_evidence='matching checksums',action='copy')
  self.plan=dict(project_gid='1218559074752632',task_gid='1218559788929226',file_plan=[self.row],recorded_at='2026-09-17T00:00:00Z',first_write_at='2026-09-17T00:01:00Z',evidence_path='actual-plan.json')
  self.before=dict(complete=True,items=[self.source])
 def test_plan(self):self.assertEqual(c.check_file_plan(self.plan,self.before),[])
 def test_wrong_scope(self):
  self.plan['project_gid']='other';self.assertTrue(c.check_file_plan(self.plan,self.before))
 def test_wrong_type(self):
  self.source['name']='01.pdf';self.row['planned_path']='ZVIM-LAF-Photoshop-Source-Files/01.pdf';self.assertTrue(c.check_file_plan(self.plan,self.before))
 def test_renaming_rejected(self):
  self.row['planned_path']='ZVIM-LAF-Photoshop-Source-Files/new.psd';self.assertTrue(c.check_file_plan(self.plan,self.before))
 def test_not_content_inspected(self):
  self.row['inspected']=True;self.assertTrue(c.check_file_plan(self.plan,self.before))
 def test_integrity_still_required(self):
  # Isolate the completion evidence checks from separate inventory validation.
  old=c.check;c.check=lambda *a:dict(issues=[],active_files=2,maximum_path_length=60)
  try:
   out=copy.deepcopy(self.source);out['id']='copy'
   data=dict(root_ancestry=[dict(id='drive',name='Drive'),dict(id='project',name='Project')],before=self.before,after=dict(complete=True,items=[self.source,out]),plan=self.plan,file_evidence=[self.row])
   self.assertTrue(c.check_completion(data)['passed'])
   out['md5Checksum']='changed'
   self.assertIn('active_content_mismatch',[x['type'] for x in c.check_completion(data)['issues']])
  finally:c.check=old
if __name__=='__main__':unittest.main()
