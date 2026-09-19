import unittest,tempfile,json
from pathlib import Path
import reviewed_folder_corrections as g

class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.writes=[];self.fail=False
  def f(i,n,p):return {'id':i,'name':n,'parents':[p] if p else [],'driveId':g.DRIVE,'mimeType':'application/vnd.google-apps.folder','trashed':False}
  self.f=f;self.fid=next(iter(g.RENAMES));self.mid=next(iter(g.MOVES))
  self.data={g.INCANMORE:f(g.INCANMORE,'root',None),'parent':f('parent','ZVIM-InCanmore-Source-Files',g.INCANMORE),self.fid:f(self.fid,g.RENAMES[self.fid][0],'parent'),g.LAUGHS:f(g.LAUGHS,'laughs',None),g.ARCHIVE:f(g.ARCHIVE,'Archive',g.LAUGHS),self.mid:f(self.mid,g.MOVES[self.mid],g.LAUGHS)}
 def tearDown(self):self.temp.cleanup()
 def call(self,*a):
  if a[0]=='get':return {'file':dict(self.data[a[1]])}
  if a[0]=='ls':return {'files':[dict(v) for v in self.data.values() if v['parents']==[a[2]]]}
  self.writes.append(a)
  if self.fail:raise TimeoutError('uncertain')
  if a[0]=='rename':self.data[a[1]]['name']=a[2]
  else:self.data[a[1]]['parents']=[a[3]]
  return {'file':dict(self.data[a[1]])}
 def rename(self):return g.apply(self.base,g.INCANMORE,('rename',self.fid,g.RENAMES[self.fid][1]),self.call)
 def test_rename_idempotent(self):
  self.rename();self.rename();self.assertEqual(len(self.writes),1);self.assertEqual(self.data[self.fid]['parents'],['parent'])
 def test_scope(self):
  with self.assertRaises(ValueError):g.apply(self.base,g.INCANMORE,('rename',self.fid,'anything'),self.call)
  self.assertFalse(self.writes)
 def test_parent(self):
  self.data['parent']['parents']=['outside']
  with self.assertRaises(ValueError):self.rename()
  self.assertFalse(self.writes)
 def test_collision(self):
  self.data['other']=self.f('other',g.RENAMES[self.fid][1],'parent')
  with self.assertRaises(ValueError):self.rename()
  self.assertFalse(self.writes)
 def test_uncertain_not_replayed(self):
  self.fail=True
  with self.assertRaises(TimeoutError):self.rename()
  self.fail=False
  with self.assertRaises(RuntimeError):self.rename()
  self.assertEqual(len(self.writes),1)
 def test_move_empty_tree(self):
  self.data['empty']=self.f('empty','original child',self.mid)
  g.apply(self.base,g.LAUGHS,('move',self.mid,'--parent',g.ARCHIVE),self.call)
  self.assertEqual(self.data[self.mid]['parents'],[g.ARCHIVE]);self.assertEqual(self.data['empty']['parents'],[self.mid])
 def test_move_nonempty_rejected(self):
  self.data['file']=dict(self.f('file','document',self.mid),mimeType='application/pdf')
  with self.assertRaises(ValueError):g.apply(self.base,g.LAUGHS,('move',self.mid,'--parent',g.ARCHIVE),self.call)
  self.assertFalse(self.writes)
if __name__=='__main__':unittest.main()

