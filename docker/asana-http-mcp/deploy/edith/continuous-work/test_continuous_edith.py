import json
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import continuous_edith as c

class ContinuousTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'dispatch'
        self.root.mkdir()
        self.gid = '1234567890123456'
        self.nxt = '1234567890123457'
        self.current = {'completed': False, 'assignee': {'gid':'edith'}}
        self.backup = {'name':'[Edith dispatch] Continue saved work after '+self.gid, 'completed':False,'assignee':None}
        self.writes=[]; self.pauses=[]; self.comments=[]; self.commands=[]
        def save(gid, data): (self.root/(gid+'.json')).write_text(json.dumps(data))
        def call(name,args):
            self.assertEqual(name,'asana_update_task')
            self.writes.append(args)
            self.backup['due_at']=args['due_at']
        self.d=types.SimpleNamespace(ROOT=self.root, EDITH='edith', save=save,
            connect=lambda:None, get_task=lambda gid:self.current if gid==self.gid else self.backup,
            call=call, pause=lambda gid:self.pauses.append(gid), comment=lambda *args:self.comments.append(args))
        save(self.gid,{'next_task':self.nxt})
        (self.root/(self.gid+'.prompt.txt')).write_text('Initial verified scope')

    def run_worker(self, codes, complete_on=None, fingerprints=None):
        owner=self
        class Process:
            pid=99999999
            def __init__(self,args,**kw):
                owner.commands.append(args); self.returncode=codes[len(owner.commands)-1]
            def communicate(self,**kw):
                if complete_on == len(owner.commands): owner.current['completed']=True
                return ('{}','')
        lockfile=tempfile.TemporaryFile(mode='a+')
        self.addCleanup(lockfile.close)
        with patch.object(c.subprocess,'Popen',Process), patch.object(c.time,'sleep'), \
             patch.object(c,'progress_fingerprint',side_effect=fingerprints or ['a']*10), \
             patch.dict('sys.modules',{'ready_review_handoff':types.SimpleNamespace(edith_release=lambda:{'status':'no-ready-review'})}):
            c.run_continuous(self.d,self.gid,os.dup(lockfile.fileno()))
        return json.loads((self.root/(self.gid+'.json')).read_text())

    def test_normal_continuation_reuses_task_and_session(self):
        r=self.run_worker([0,0],complete_on=2,fingerprints=['a','b','b'])
        self.assertEqual(r['status'],'continuous-finished')
        self.assertEqual(len(self.commands),2)
        self.assertEqual(self.commands[0][self.commands[0].index('--session-key')+1],self.commands[1][self.commands[1].index('--session-key')+1])
        self.assertTrue(all(w['task_id']==self.nxt for w in self.writes))
        self.assertEqual(self.pauses,[self.gid])

    def test_failed_turn_does_not_replay_or_cancel_recovery(self):
        r=self.run_worker([1])
        self.assertEqual(r['status'],'continuous-failed-recovery-armed')
        self.assertEqual(len(self.commands),1)
        self.assertEqual(self.pauses,[])

    def test_no_progress_stops_usage_loop(self):
        r=self.run_worker([0,0])
        self.assertEqual(r['status'],'continuous-paused-no-production-progress')
        self.assertEqual(len(self.commands),2)
        self.assertEqual(self.pauses,[self.gid])
        self.assertEqual(len(self.comments),1)

    def test_assigned_backup_blocks_launch(self):
        self.backup['assignee']={'gid':'edith'}
        with self.assertRaises(AssertionError):self.run_worker([])
        self.assertEqual(self.commands,[])

    def test_changed_owner_blocks_launch(self):
        self.current['assignee']={'gid':'other'}
        with self.assertRaises(AssertionError):self.run_worker([])
        self.assertEqual(self.writes,[])

    def test_backup_date_readback_required(self):
        self.d.call=lambda *args:self.backup.update(due_at='2000-01-01T00:00:00Z')
        with self.assertRaises(AssertionError): c.renew_backup(self.d,self.gid,{'next_task':self.nxt})

    def test_status_timestamp_is_not_progress(self):
        work=Path(self.tmp.name)/'folder-cleanup';work.mkdir()
        p=work/'queue-checkpoint.json';p.write_text('old')
        a=c.progress_fingerprint(work);p.write_text('new')
        self.assertEqual(a,c.progress_fingerprint(work))
        (work/'execution-state.json').write_text('{"copy":"verified"}')
        self.assertNotEqual(a,c.progress_fingerprint(work))

if __name__=='__main__':unittest.main()

