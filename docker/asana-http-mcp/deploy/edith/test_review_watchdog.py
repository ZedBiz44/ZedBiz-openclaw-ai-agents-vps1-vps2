import unittest
from datetime import datetime, timezone
from review_watchdog import overdue_reviews, RUBY


class WatchdogTests(unittest.TestCase):
    def test_missed_assignment_and_missed_email_are_detected(self):
        base={'name':'[Ruby review] Ready review','completed':False,'due_at':'2026-09-17T20:00:00Z'}
        rows=[{**base,'gid':'unassigned','assignee':None},{**base,'gid':'assigned','assignee':{'gid':RUBY}}]
        found=overdue_reviews(rows,datetime(2026,9,17,20,30,tzinfo=timezone.utc))
        self.assertEqual({x['gid'] for x in found},{'assigned','unassigned'})

    def test_safe_non_actionable_states_do_not_escalate(self):
        base={'name':'[Ruby review] Ready review','completed':False,'due_at':'2026-09-17T20:00:00Z','assignee':None}
        rows=[{**base,'completed':True},{**base,'name':'[Ruby review] Pilot check'},
              {**base,'due_at':'2026-09-17T21:00:00Z'},{**base,'due_at':None},
              {**base,'assignee':{'gid':'someone-else'}},{**base,'name':'Folder outcome'}]
        self.assertEqual(overdue_reviews(rows,datetime(2026,9,17,20,31,tzinfo=timezone.utc)),[])


if __name__=='__main__':unittest.main()
