import unittest,tempfile,zipfile
from pathlib import Path
from native_document_verification import package_content

class NativeTests(unittest.TestCase):
    def test_metadata_only_is_not_content(self):
        with tempfile.TemporaryDirectory() as d:
            files=[]
            for n in range(2):
                p=Path(d)/str(n)
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr('word/document.xml','<doc>hello</doc>')
                    z.writestr('word/media/image.png',b'abc')
                    z.writestr('docProps/core.xml',str(n))
                files.append(p)
            self.assertEqual(*map(package_content,files))
            with zipfile.ZipFile(files[1],'a') as z:z.writestr('word/footer.xml','lost text')
            self.assertNotEqual(*map(package_content,files))
    def test_content_and_media_changes_detected(self):
        with tempfile.TemporaryDirectory() as d:
            values=[]
            for text,image in [('hello',b'abc'),('changed',b'abc'),('hello',b'xyz')]:
                p=Path(d)/str(len(values))
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr('word/document.xml',text)
                    z.writestr('word/media/image.png',image)
                values.append(package_content(p))
            self.assertNotEqual(values[0],values[1]);self.assertNotEqual(values[0],values[2])

if __name__=='__main__':unittest.main()

