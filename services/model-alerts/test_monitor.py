import unittest
import monitor


class Alerts(unittest.TestCase):
    def test_one_failure_and_delayed_proven_recovery(self):
        s = {}
        self.assertEqual(monitor.transition(s, [(100, 'failure', 'auth')], 100), 'failure')
        monitor.acknowledge(s, 'failure')
        self.assertIsNone(monitor.transition(s, [(110, 'fallback', 'backup')], 110))
        self.assertIsNone(monitor.transition(s, [(120, 'success', '')], 120))
        self.assertEqual(monitor.transition(s, [], 231), 'recovery')
        monitor.acknowledge(s, 'recovery')
        self.assertIsNone(monitor.transition(s, [], 240))

    def test_failed_delivery_stays_pending(self):
        s = {}
        self.assertEqual(monitor.transition(s, [(100, 'failure', 'auth')], 100), 'failure')
        self.assertEqual(monitor.transition(s, [], 160), 'failure')

    def test_old_success_does_not_clear_new_failure(self):
        s = {'announced': True, 'failure': 200}
        self.assertIsNone(monitor.transition(s, [(100, 'success', '')], 400))

    def test_parser_only_selected_primary_and_new_events(self):
        text = '''2026-09-07T16:34:25-06:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.6-sol candidate=openai/gpt-5.6-sol reason=unknown detail=auth refresh request failed
2026-09-07T16:34:26-06:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.6-sol candidate=openai/gpt-5.6-terra reason=unknown
2026-09-07T16:34:27-06:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.6-sol candidate=openrouter/google/gemini-3.1-flash-lite reason=unknown'''
        events = monitor.log_events(text, 'openai/gpt-5.6-sol', 0)
        self.assertEqual([e[1] for e in events], ['failure', 'fallback'])
        self.assertIn('sign-in', events[0][2])
        self.assertEqual(monitor.log_events(text, 'openai/gpt-5.6-sol', events[-1][0]), [])
        self.assertEqual(monitor.log_events(text, 'different/model', 0), [])


if __name__ == '__main__':
    unittest.main()
