import copy,tempfile,unittest
from pathlib import Path
import folder_rename_correction as m
class Check(unittest.TestCase):
 def setup_call(self):
  self.folder={'id':m.FOLDER,'name':m.OLD,'mimeType':'application/vnd.google-apps.folder','parents':[m.ROOT],'driveId':m.DRIVE}
  self.child={'id':m.CHILD,'name':'ZVIM-Whiteboard-Research','parents':[m.FOLDER],'driveId':m.DRIVE};self.writes=0
  def call(*a):
   if a[0]=='get':return {'file':copy.deepcopy(self.folder if a[1]==m.FOLDER else self.child)}
   if a[0]=='ls':return {'files':[copy.deepcopy(self.folder)]}
   if a[0]=='rename':self.writes+=1;self.folder['name']=a[2];return {}
   raise AssertionError(a)
  return call
 def test_once(self):
  call=self.setup_call()
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(m.rename(d,m.ROOT,('rename',m.FOLDER,m.NEW),call)['status'],'renamed-and-verified')
   m.rename(d,m.ROOT,('rename',m.FOLDER,m.NEW),call);self.assertEqual(self.writes,1)
 def test_wrong_scope(self):
  call=self.setup_call()
  with tempfile.TemporaryDirectory() as d:
   for args in [('rename',m.CHILD,m.NEW),('rename',m.FOLDER,'Other'),('rename',m.FOLDER,m.NEW,'--force')]:
    with self.assertRaises(ValueError):m.rename(d,m.ROOT,args,call)
   self.assertEqual(self.writes,0)
 def test_changed_parent(self):
  call=self.setup_call();self.child['parents']=['other']
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.rename(d,m.ROOT,('rename',m.FOLDER,m.NEW),call)
   self.assertEqual(self.writes,0)
 def test_uncertain_write(self):
  real=self.setup_call()
  def call(*a):
   result=real(*a)
   if a[0]=='rename':raise TimeoutError('ack lost')
   return result
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(TimeoutError):m.rename(d,m.ROOT,('rename',m.FOLDER,m.NEW),call)
   self.assertEqual(m.rename(d,m.ROOT,('rename',m.FOLDER,m.NEW),real)['status'],'verified-existing')
   self.assertEqual(self.writes,1)
if __name__=='__main__':unittest.main()
