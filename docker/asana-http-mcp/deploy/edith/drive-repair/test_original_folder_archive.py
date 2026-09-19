import unittest
from original_folder_archive import validate_plan
class Tests(unittest.TestCase):
 def setUp(self):
  self.before={'items':[{'id':'old','name':'Research','parents':['root'],'mimeType':'application/vnd.google-apps.folder'},{'id':'f','parents':['old'],'mimeType':'application/pdf','md5Checksum':'abc','size':'2'}]}
  self.plan={'file_plan':[{'source_id':'f','action':'copy'}],'folder_archive_plan':[{'source_id':'old','source_name':'Research','archive_path':'Z-Archive'}]}
  self.review={'archive_paths':['Z-Archive']};self.state={'folders':{'Z-Archive':'archive'},'copies':{'f':{'active_id':'active','permissions_matched':True,'content_read':'verified','md5Checksum':'abc','size':'2'}},'archived':['f']}
 def check(self,protected=set()):return validate_plan(self.plan,self.before,self.review,self.state,'root',('move','old','--parent','archive'),protected)
 def test_valid(self):self.check()
 def test_unplanned(self):
  self.plan['folder_archive_plan']=[]
  with self.assertRaises(ValueError):self.check()
 def test_unfinished(self):
  self.state['archived']=[]
  with self.assertRaises(ValueError):self.check()
 def test_held(self):
  self.plan['file_plan'][0]['action']='hold'
  with self.assertRaises(ValueError):self.check()
 def test_protected_descendant(self):
  with self.assertRaises(ValueError):self.check({'f'})
 def test_wrong_destination(self):
  self.state['folders']['Z-Archive']='other'
  with self.assertRaises(ValueError):self.check()
if __name__=='__main__':unittest.main()

