import ctypes
import ctypes.util
import json
import subprocess
import unittest
from unittest.mock import patch
import monitor


class Repair(unittest.TestCase):
    def packed(self, raw):
        lib = ctypes.CDLL(ctypes.util.find_library('zstd'))
        lib.ZSTD_compress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
        lib.ZSTD_compress.restype = ctypes.c_size_t
        out = ctypes.create_string_buffer(len(raw) + 1024)
        n = lib.ZSTD_compress(out, len(out), raw, len(raw), 1)
        return out.raw[:n]

    def test_plain(self):
        self.assertEqual(monitor.decode_event('{"message":{}}', None, None), {'message': {}})

    def test_compressed(self):
        raw = json.dumps({'message': {'content': 'hello' * 2000}}).encode()
        self.assertEqual(monitor.decode_event(None, self.packed(raw), len(raw)), json.loads(raw))

    def test_corrupt(self):
        with self.assertRaises(monitor.MonitoringReadError):
            monitor.decode_event(None, b'broken', 100)

    def test_size_mismatch(self):
        with self.assertRaises(monitor.MonitoringReadError):
            monitor.decode_event(None, self.packed(b'{}'), 3)

    def test_bad_bounds(self):
        for size in [None, -1, 4194305]:
            with self.assertRaises(monitor.MonitoringReadError):
                monitor.decode_event(None, b'x', size)

    def test_invalid_json(self):
        with self.assertRaises(monitor.MonitoringReadError):
            monitor.decode_event('private invalid text', None, None)

    def test_errors_do_not_expose_command_or_transcript(self):
        e = subprocess.CalledProcessError(1, ['secret'], stderr='private text')
        self.assertEqual(monitor.read_failure(e), 'monitor command failed (exit 1)')

    def test_failed_period_is_retried_then_recovered(self):
        state = {'cursor': 90, 'last_probe': 100}
        sent = []
        cfg = {'mode': 'docker', 'agents': {'sample': '/root'}, 'host': 'test'}
        calls = []
        failure = subprocess.CalledProcessError(1, [], stderr='MONITOR_READ_ERROR: compressed transcript decode or size check failed')
        def bad(cmd, **kw):
            calls.append(cmd)
            raise failure
        def sender(cfg, text, nonce):
            sent.append(text)
            return 'test'
        with patch.object(monitor.time, 'time', return_value=100), patch.object(monitor.subprocess, 'run', side_effect=bad):
            monitor.run(cfg, state, sender)
        self.assertIn('Monitoring check failed', sent[0])
        with patch.object(monitor.time, 'time', return_value=5000), patch.object(monitor.subprocess, 'run', side_effect=bad):
            monitor.run(cfg, state, sender)
        self.assertEqual(calls[-1][calls[-1].index('--since')+1], '90')
        self.assertEqual(len(sent), 1)
        def good(cmd, **kw):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, json.dumps({'primary':'x/y','success':0,'oauth':None}) if '--collect' in cmd else '', '')
        with patch.object(monitor.time, 'time', return_value=5201), patch.object(monitor.subprocess, 'run', side_effect=good):
            monitor.run(cfg, state, sender)
        self.assertIn('failed period was successfully reread', sent[-1])
        self.assertNotIn('retry_since', state['agents']['sample'])

    def test_actual_service_failure_still_alerts(self):
        cfg = {'mode':'native', 'agents':{'sample':'/root'}, 'host':'test'}
        sent=[]
        with patch.object(monitor.subprocess, 'run', return_value=subprocess.CompletedProcess([], 3)):
            monitor.run(cfg, {}, lambda c,t,n: sent.append(t) or 'test')
        self.assertIn('systemd service is not active', sent[0])


if __name__ == '__main__':
    unittest.main()
