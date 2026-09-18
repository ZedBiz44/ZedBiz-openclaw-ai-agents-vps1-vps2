import sys,unittest,copy
sys.path.insert(0,'/home/node/.openclaw/workspace/skills/z-files-folders/scripts')
sys.path.insert(0,'/tmp')
import check_completion_packages as c
from fast_continuation import expedite_successor
from datetime import datetime,timezone
class Tests(unittest.TestCase):
 def setUp(self):
  self.root=dict(id='root',name='Old-Web',path='Old-Web',mimeType='application/vnd.google-apps.folder',parents=['main'])
  self.source=dict(id='js',name='app.js',path='Old-Web/js/app.js',parents=['sub'],mimeType='text/javascript',size='10',md5Checksum='abc')
  self.sub=dict(id='sub',name='js',path='Old-Web/js',parents=['root'],mimeType='application/vnd.google-apps.folder')
  self.pdf=dict(id='pdf',name='guide.pdf',path='Old-Web/guide.pdf',parents=['root'],mimeType='application/pdf',size='20',md5Checksum='def')
  self.before=dict(complete=True,items=[self.root,self.sub,self.source,self.pdf])
  self.row=dict(source_id='js',package_root_id='root',preservation_exception=c.PACKAGE_POLICY,inspected=False,planned_path='ZVIM-Retained-Packages/Old-Web/js/app.js',inspection_method='metadata-only: user-approved package preservation',inspection_evidence='listing receipt',purpose='Old website package',classification_reason='Retain support files',action='copy')
  self.doc=dict(source_id='pdf',planned_path='Documents/guide.pdf',inspection_method='own PDF content read',inspection_evidence='actual text',purpose='Useful guide',classification_reason='Readable reference',action='copy')
  self.package=dict(root_id='root',kind='saved-website',purpose='Old website',listing_evidence='listing.json',document_triage='listed',useful_documents=['pdf'],planned_root='ZVIM-Retained-Packages/Old-Web')
  self.plan=dict(project_gid='1218559074752632',task_gid='1218559788929226',file_plan=[self.row,self.doc],preserved_packages=[self.package])
 def valid(self):return c.preservation_exception(self.row,self.plan,self.source,self.before)
 def test_package_preserved(self):self.assertTrue(self.valid());self.assertEqual(c.check_file_plan(self.plan,self.before),[])
 def test_pdf_not_exempt(self):self.assertFalse(c.package_exception(dict(self.row,source_id='pdf',planned_path='ZVIM-Retained-Packages/Old-Web/guide.pdf'),self.plan,self.pdf,self.before))
 def test_missing_document_triage(self):self.package['useful_documents']=[];self.assertFalse(self.valid())
 def test_renaming_rejected(self):self.row['planned_path']='ZVIM-Retained-Packages/Old-Web/app.js';self.assertFalse(self.valid())
 def test_wrong_ancestry(self):self.source['parents']=['elsewhere'];self.assertFalse(self.valid())
 def test_wrong_scope(self):self.plan['project_gid']='other';self.assertFalse(self.valid())
 def test_opaque_zip_deferred(self):
  self.source.update(id='zip',name='old.zip',path='old.zip',parents=['main'])
  self.row.update(source_id='zip',package_root_id='zip',planned_path='ZVIM-Retained-Packages/old.zip')
  self.package.update(root_id='zip',kind='archive',document_triage='deferred-encrypted',defer_reason='Directory encrypted',useful_documents=[])
  self.assertTrue(self.valid())
 def test_false_inspection(self):self.row['inspected']=True;self.assertFalse(self.valid())
 def timing(self,code=0,complete=True,assigned=False):
  nxt=dict(name='[Edith dispatch] Continue saved work after old',completed=False,assignee={'gid':'edith'} if assigned else None,due_at='2026-09-18T01:00:00Z')
  writes=[]
  def update(gid,due):writes.append((gid,due));nxt['due_at']=due
  result=expedite_successor(dict(task='old',next_task='next',exit_code=code),dict(completed=complete),lambda gid:nxt,update,datetime(2026,9,18,0,45,tzinfo=timezone.utc))
  return result,writes
 def test_success_expedites_existing(self):self.assertEqual(self.timing()[0]['status'],'successor-expedited');self.assertEqual(len(self.timing()[1]),1)
 def test_failure_keeps_backup(self):self.assertEqual(self.timing(code=124)[1],[])
 def test_unconfirmed_keeps_backup(self):self.assertEqual(self.timing(complete=False)[1],[])
 def test_already_assigned_no_retime(self):self.assertEqual(self.timing(assigned=True)[1],[])
if __name__=='__main__':unittest.main()


