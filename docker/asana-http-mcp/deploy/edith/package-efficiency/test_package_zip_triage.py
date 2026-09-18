import tempfile,unittest,zipfile
from pathlib import Path
from package_zip_triage import triage
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.z=self.root/'bundle.zip'
  with zipfile.ZipFile(self.z,'w') as z:z.writestr('docs/guide.pdf',b'%PDF example');z.writestr('js/app.js','do not run')
 def tearDown(self):self.temp.cleanup()
 def test_list_and_selected_extract(self):
  result=triage(self.z,self.root/'out',['docs/guide.pdf'])
  self.assertEqual(result['useful_documents'],['docs/guide.pdf']);self.assertEqual(len(result['extracted']),1);self.assertFalse((self.root/'out/js').exists())
 def test_no_script_extract(self):
  with self.assertRaises(ValueError):triage(self.z,self.root/'out',['js/app.js'])
 def test_no_overwrite(self):
  triage(self.z,self.root/'out',['docs/guide.pdf'])
  with self.assertRaises(FileExistsError):triage(self.z,self.root/'out',['docs/guide.pdf'])
 def test_traversal(self):
  with zipfile.ZipFile(self.z,'w') as z:z.writestr('../escape.pdf','bad')
  with self.assertRaises(ValueError):triage(self.z,self.root/'out',['../escape.pdf'])
 def test_unsupported(self):
  self.z.write_text('not a zip');self.assertEqual(triage(self.z,self.root/'out')['status'],'deferred-unsupported')
if __name__=='__main__':unittest.main()
