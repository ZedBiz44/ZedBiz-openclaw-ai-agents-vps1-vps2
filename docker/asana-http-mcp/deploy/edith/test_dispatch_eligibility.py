import unittest
from datetime import datetime, timezone
from dispatch_eligibility import eligible


class EligibilityTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,17,20,0,tzinfo=timezone.utc)
        self.task={'assignee':{'gid':'edith'},'resource_subtype':'default_task','completed':False,'due_at':'2026-09-17T19:59:00Z','dependencies':[]}

    def check(self,dep=None): return eligible(self.task,'edith',lambda _:dep,self.now)

    def test_due_work(self): self.assertEqual(self.check(),'eligible')
    def test_future(self):
        self.task['due_at']='2026-09-17T21:00:00Z';self.assertEqual(self.check(),'not-yet-due')
    def test_completed(self):
        self.task['completed']=True;self.assertEqual(self.check(),'already-completed')
    def test_wrong_owner(self):
        self.task['assignee']={'gid':'other'};self.assertEqual(self.check(),'wrong-assignee')
    def test_approval_is_not_sitting(self):
        self.task['resource_subtype']='approval';self.assertEqual(self.check(),'not-a-work-sitting')
    def test_incomplete_dependency(self):
        self.task['dependencies']=[{'gid':'dep'}];self.assertEqual(self.check({'resource_subtype':'default_task','completed':False}),'dependency-incomplete')
    def test_approval_outcomes(self):
        self.task['dependencies']=[{'gid':'dep'}]
        for status in ['pending','rejected','changes_requested',None]:
            with self.subTest(status=status): self.assertEqual(self.check({'resource_subtype':'approval','completed':True,'approval_status':status}),'dependency-not-approved')
        self.assertEqual(self.check({'resource_subtype':'approval','completed':True,'approval_status':'approved'}),'eligible')


if __name__=='__main__': unittest.main()
