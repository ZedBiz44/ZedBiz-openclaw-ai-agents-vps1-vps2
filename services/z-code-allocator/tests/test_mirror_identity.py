import os
import tempfile
import unittest
from app.mirror_worker import NotionMirror

CODE = 'ZMMW-40000-100007-010'

class FakeMirror(NotionMirror):
    def __init__(self):
        super().__init__('not-a-token', 'registry', 'topics')
        self.pages = {}
        self.creates = 0
        self.fail_create = False
        self.indexed = False

    def _request(self, method, path, payload=None, **kwargs):
        if path.endswith('/query'):
            return {'results': list(self.pages.values()) if self.indexed else [], 'has_more': False}
        if method == 'GET': return self.pages[path.split('/')[-1]]
        if method == 'PATCH':
            page = self.pages[path.split('/')[-1]]
            page['properties'] = payload['properties']
            return page
        self.creates += 1
        page = {'id':str(self.creates),'parent':payload['parent'],'properties':payload['properties']}
        self.pages[page['id']] = page
        if self.fail_create: raise TimeoutError('response lost')
        return page

class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ['ZCODE_MIRROR_IDENTITY_PATH'] = self.tmp.name + '/cache.sqlite3'
        self.m = FakeMirror()

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop('ZCODE_MIRROR_IDENTITY_PATH')

    def create(self, code=CODE):
        return self.m.request('POST','/pages',{'parent':{'database_id':'registry'},'properties':{'Z-Code':self.m.text(code)}})

    def test_delayed_index_and_restart_preserve_identity(self):
        self.assertIsNone(self.m.find_page(CODE))
        page = self.create()
        self.assertEqual(self.m.find_page(CODE), page['id'])
        newer = FakeMirror()
        newer.pages = self.m.pages
        self.assertEqual(newer.find_page(CODE),page['id'])
        self.create()
        self.assertEqual(self.m.creates,1)

    def test_uncertain_create_cannot_repeat(self):
        self.m.fail_create=True
        with self.assertRaises(TimeoutError): self.create()
        with self.assertRaisesRegex(RuntimeError,'outcome unknown'): self.create()
        with self.assertRaisesRegex(RuntimeError,'outcome unknown'): self.m.find_page(CODE)
        self.m.indexed=True
        self.assertEqual(self.m.find_page(CODE),'1')
        self.assertEqual(self.m.creates,1)

    def test_archived_identity_requires_review(self):
        page=self.create()
        page['archived']=True
        with self.assertRaisesRegex(RuntimeError,'identity changed'): self.m.find_page(CODE)

    def test_topic_identity(self):
        record={'z_knowledge_core':'ZMMW','knowledge_lane':'40000','topic_identifier':'100007','name_key':'example'}
        self.m.request('POST','/pages',{'parent':{'database_id':'topics'},'properties':{'Topic-Key':self.m.text('ZMMW-40000-100007')}})
        self.assertEqual(self.m.find_topic_page(record),'1')

    def test_other_lanes_unchanged(self):
        self.create('Z1PS-30001-100006-010')
        self.assertIsNone(self.m.find_page('Z1PS-30001-100006-010'))

if __name__ == '__main__': unittest.main()
