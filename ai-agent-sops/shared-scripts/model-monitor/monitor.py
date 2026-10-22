#!/usr/bin/env python3
"""Host-local OpenClaw model alerts. Python standard library; no AI calls."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo
NOTICE_HEADER = '**ZedBiz Model Monitor — Automatic Fleet Notice**'

def read_db(path):
    return sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True, timeout=10)



class MonitoringReadError(RuntimeError):
    pass


def decode_event(raw, packed, size):
    """Match OpenClaw's zstd payload bounds; never emit transcript contents."""
    if raw is None:
        import ctypes
        import ctypes.util
        if (not isinstance(packed, bytes) or not 0 < len(packed) <= 4194304
                or not isinstance(size, int) or not 0 < size <= 4194304):
            raise MonitoringReadError('invalid compressed transcript bounds')
        library = ctypes.util.find_library('zstd')
        if not library:
            raise MonitoringReadError('zstd decoder unavailable')
        lib = ctypes.CDLL(library)
        lib.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
        lib.ZSTD_decompress.restype = ctypes.c_size_t
        lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
        lib.ZSTD_isError.restype = ctypes.c_uint
        out = ctypes.create_string_buffer(size)
        count = lib.ZSTD_decompress(out, size, packed, len(packed))
        if lib.ZSTD_isError(count) or count != size:
            raise MonitoringReadError('compressed transcript decode or size check failed')
        raw = out.raw
    try:
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError()
        return event
    except (ValueError, TypeError, UnicodeError):
        raise MonitoringReadError('invalid transcript JSON') from None


def read_since(agent, default):
    # Once a read fails, do not slide past it, even after an hour or restart.
    return agent.get('retry_since', default)


def read_failure(exc):
    if isinstance(exc, subprocess.CalledProcessError):
        # Only our deliberately sanitized diagnostic is safe to retain.
        for line in (exc.stderr or '').splitlines():
            if line.startswith('MONITOR_READ_ERROR:'):
                return line[len('MONITOR_READ_ERROR:'):].strip()
        return 'monitor command failed (exit %s)' % exc.returncode
    if isinstance(exc, MonitoringReadError):
        return str(exc)
    return 'monitor read failed (%s)' % type(exc).__name__


def collect(root, since, probe):
    """Runs within the actual agent filesystem; returns no credential material."""
    root = Path(root)
    cfg = json.loads((root / 'openclaw.json').read_text())
    agents = cfg.get('agents', {})
    entry = agents.get('entries', {}).get('main', {})
    model = entry.get('model', agents.get('defaults', {}).get('model', {}))
    primary = model if isinstance(model, str) else model.get('primary', '')
    result = {'primary': primary, 'success': 0, 'oauth': None}
    with read_db(root / 'agents/main/agent/openclaw-agent.sqlite') as db:
        columns = {r[1] for r in db.execute('PRAGMA table_info(transcript_events)')}
        payload = 'event_zstd,event_utf8_bytes' if 'event_zstd' in columns else 'NULL,NULL'
        for raw, packed, size, created, seq in db.execute(
            'SELECT event_json,' + payload + ',created_at,seq FROM transcript_events WHERE created_at>=?',
            (int(since * 1000),),
        ):
            try:
                event = decode_event(raw, packed, size)
            except MonitoringReadError as exc:
                raise MonitoringReadError('%s; created_at=%s seq=%s' % (exc, created, seq)) from None
            m = event.get('message', {})
            if (m.get('role') == 'assistant' and m.get('stopReason') == 'stop'
                    and m.get('provider', '') + '/' + m.get('model', '') == primary):
                result['success'] = max(result['success'], created / 1000)
    if probe and primary.startswith('openai/'):
        profiles = {}
        with read_db(root / 'state/openclaw.sqlite') as db:
            row = db.execute("SELECT value_json FROM config_machine_state WHERE state_key='authProfiles.store'").fetchone()
            if row:
                profiles.update(json.loads(row[0]).get('profiles', {}))
        with read_db(root / 'agents/main/agent/openclaw-agent.sqlite') as db:
            for row in db.execute('SELECT store_json FROM auth_profile_store'):
                profiles.update(json.loads(row[0]).get('profiles', {}))
        order = cfg.get('auth', {}).get('order', {}).get('openai', list(profiles))
        credential = next((profiles[k] for k in order if k in profiles
                           and profiles[k].get('type') == 'oauth'), None)
        if credential:
            req = urllib.request.Request(
                'https://chatgpt.com/backend-api/codex/models?client_version=0.151.0',
                headers={'Authorization': 'Bearer ' + credential['access'],
                         'ChatGPT-Account-Id': credential['accountId'],
                         'User-Agent': 'codex_cli_rs/0.151.0'},
            )
            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    result['oauth'] = 'accepted' if response.status == 200 else 'unknown'
            except urllib.error.HTTPError as exc:
                try:
                    code = json.loads(exc.read()).get('error', {}).get('code')
                except (ValueError, AttributeError):
                    code = None
                # Expiry can be repaired by normal refresh. Only proven revocation alerts here.
                result['oauth'] = 'revoked' if code == 'token_revoked' else 'unknown'
            except (OSError, TimeoutError):
                result['oauth'] = 'unknown'
    return result


def log_events(lines, primary, since, context=None):
    context = context if context is not None else {}
    if context.get("primary") != primary:
        context.clear()
        context["primary"] = primary
    records = []
    for line in lines.splitlines():
        stamp = re.search(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d))', line)
        if not stamp:
            continue
        when = dt.datetime.fromisoformat(stamp[1].replace('Z', '+00:00')).timestamp()
        if when <= max(since, context.get("last_seen", 0)):
            continue
        fields = dict(re.findall(r'(requested|candidate|decision|reason)=([^\s]+)', line))
        if fields.get('requested') == primary:
            records.append((when, line, fields))
    events = []
    rooted_cleanup_chain = context.get("rooted_cleanup_chain", False)
    actual_primary_failure = context.get("actual_primary_failure", False)
    for when, line, fields in sorted(records, key=lambda item: item[0]):
        decision = fields.get('decision')
        candidate = fields.get('candidate')
        rooted_rejection = (
            'collection review requires a runtime that enforces the workshop root'
            in line.lower()
        )
        if decision == 'candidate_failed' and rooted_rejection:
            # Workshop collection cleanup rejects runtimes that cannot enforce its
            # private folder boundary. Suppress the complete root-only fallback
            # chain, including its eventual compatible-model success.
            rooted_cleanup_chain = True
            continue
        if decision == 'candidate_failed' and candidate == primary:
            actual_primary_failure = True
            reason = 'Primary model request failed'
            lower = line.lower()
            if 'auth' in lower or 'token_revoked' in lower:
                reason = 'Codex sign-in rejected; reconnection may be required'
            elif 'rate' in lower or '429' in lower:
                reason = 'Primary model rate limit reached'
            events.append((when, 'failure', reason))
        elif decision == 'candidate_succeeded':
            if candidate == primary:
                events.append((when, 'success', ''))
            elif rooted_cleanup_chain and not actual_primary_failure:
                pass
            else:
                events.append((when, 'fallback', candidate or 'backup model'))
            rooted_cleanup_chain = False
            actual_primary_failure = False
    if records:
        context["last_seen"] = max(item[0] for item in records)
    context["rooted_cleanup_chain"] = rooted_cleanup_chain
    context["actual_primary_failure"] = actual_primary_failure
    return sorted(events)


def transition(state, events, now):
    """One alert per incident, and recovery only after proven success + quiet period."""
    for when, kind, value in sorted(events):
        if kind in ('failure', 'fallback'):
            state['failure'] = max(state.get('failure', 0), when)
            if kind == 'failure':
                state['reason'] = value
            else:
                state['backup'] = value
                state.setdefault('reason', 'Backup model answered; primary failure is not established')
        elif kind == 'success':
            state['success'] = max(state.get('success', 0), when)
    failure = state.get('failure', 0)
    if failure and not state.get('announced'):
        return 'failure'
    if (state.get('announced') and state.get('success', 0) > failure
            and now - failure >= 120):
        return 'recovery'
    return None


def acknowledge(state, notice):
    if notice == 'failure':
        state['announced'] = True
    else:
        retained = {key: state[key] for key in ('parser', 'service', 'primary', 'retry_since', 'collection_error', 'last_collection_error') if key in state}
        state.clear()
        state.update(retained)


def send(cfg, content, nonce):
    """Retry on next run; Discord nonce deduplicates short crash/retry windows."""
    body = {'content': content, 'allowed_mentions': {'parse': [], 'users': cfg.get('mention_users', [])},
            'nonce': nonce, 'enforce_nonce': True}
    req = urllib.request.Request(
        'https://discord.com/api/v10/channels/' + cfg['channel_id'] + '/messages',
        data=json.dumps(body).encode(), method='POST',
        headers={'Authorization': 'Bot ' + cfg['discord_token'],
                 'Content-Type': 'application/json', 'User-Agent': 'ZedBiz-Model-Monitor/1.0'},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)['id']


def run(cfg, state, sender=send):
    now = time.time()
    source = Path(__file__).read_text(encoding="utf-8")
    last = state.get('cursor', now - 60)
    # Replay a short overlap, with timestamp filtering; cap catch-up after long downtime.
    since = max(last, now - 3600)
    probe = now - state.get('last_probe', 0) >= 300
    count = 0
    for name, root in cfg['agents'].items():
        agent = state.setdefault('agents', {}).setdefault(name, {})
        agent_since = read_since(agent, since)
        try:
            if cfg['mode'] == 'docker':
                raw = subprocess.run(['docker', 'exec', '-i', name, 'python3', '-', '--collect', root,
                                      '--since', str(agent_since), *(['--probe'] if probe else [])],
                                     input=source, text=True, capture_output=True, timeout=30, check=True)
                logs = subprocess.run(['docker', 'logs', '--timestamps', '--since', str(agent_since), name],
                                      text=True, capture_output=True, timeout=15, check=True)
            else:
                active = subprocess.run(['systemctl', 'is-active', 'openclaw-' + name], capture_output=True)
                if active.returncode:
                    raise MonitoringReadError('systemd service is not active')
                raw = subprocess.run([sys.executable, __file__, '--collect', root, '--since', str(agent_since),
                                      *(['--probe'] if probe else [])],
                                     text=True, capture_output=True, timeout=30, check=True)
                logs = subprocess.run(['journalctl', '-u', 'openclaw-' + name, '--since', '@' + str(int(agent_since)),
                                       '--no-pager', '-o', 'cat'], text=True, capture_output=True, timeout=15, check=True)
            observation = json.loads(raw.stdout)
            primary = observation['primary']
            events = log_events(logs.stdout + '\n' + logs.stderr, primary, last, agent.setdefault('parser', {}))
            if observation['success']:
                events.append((observation['success'], 'success', ''))
            if observation['oauth'] == 'revoked':
                events.append((now, 'failure', 'Codex OAuth credential revoked; sign in again'))
            # Authentication acceptance alone does NOT establish successful model recovery.
            agent['primary'] = primary
            agent.pop('collection_error', None)
            agent.pop('retry_since', None)
            service_events = [(now, 'success', '')]
        except Exception as exc:
            agent.setdefault('retry_since', agent_since)
            agent['collection_error'] = read_failure(exc)
            agent['last_collection_error'] = {'at': now, 'detail': agent['collection_error'], 'retry_since': agent['retry_since']}
            print(json.dumps({'agent': name, 'monitoring_error': agent['collection_error'], 'retry_since': agent['retry_since']}), file=sys.stderr)
            service_events = [(now, 'failure', agent['collection_error'])]
            events = []
        service = agent.setdefault('service', {})
        # Migrate legacy service-only incidents without claiming model recovery.
        if agent.get('reason') == 'Agent service or monitoring read unavailable; needs checking':
            for key in ('failure', 'reason', 'announced'):
                if key in agent:
                    service[key] = agent.pop(key)
        service_notice = transition(service, service_events, now)
        if service_notice:
            label = name.capitalize() + ' · ' + cfg['host']
            detail = ('⚠️ ' + label + ' — Monitoring check failed: ' + service.get('reason', 'read unavailable') + '. Model availability remains unverified.'
                      if service_notice == 'failure' else
                      '✅ ' + label + ' — Monitoring reads restored; the failed period was successfully reread. This does not verify a new model reply.')
            text = NOTICE_HEADER + '\n' + detail
            prefix = ' '.join('<@' + u + '>' for u in cfg.get('mention_users', []))
            text = (prefix + '\n' if prefix else '') + text
            text += '\n' + dt.datetime.fromtimestamp(now, ZoneInfo('America/Edmonton')).strftime('%b %d, %I:%M %p %Z')
            try:
                message_id = sender(cfg, text, (str(int(service['failure'] * 1000)) + '-' + name + '-s' + service_notice[:1])[:25])
                acknowledge(service, service_notice)
                count += 1
                print(json.dumps({'agent': name, 'notice': 'service_' + service_notice, 'message_id': message_id}))
            except Exception as exc:
                print(json.dumps({'agent': name, 'delivery_error': type(exc).__name__}), file=sys.stderr)
        notice = transition(agent, events, now)
        if notice:
            prefix = ' '.join('<@' + u + '>' for u in cfg.get('mention_users', []))
            label = name.capitalize() + ' · ' + cfg['host']
            primary = agent.get('primary', 'configured primary')
            if notice == 'failure':
                text = f'⚠️ {label} — {agent.get("reason", "Primary model unavailable")}.\nPrimary: {primary}.'
                if agent.get('backup'):
                    text += '\nBackup observed: ' + agent['backup'] + '.'
                else:
                    text += '\nBackup use has not been confirmed by the monitor.'
            else:
                text = f'✅ {label} — Primary model recovered.\nVerified a successful reply using {primary}.'
            text = NOTICE_HEADER + '\n' + text
            text += '\n' + dt.datetime.fromtimestamp(now, ZoneInfo('America/Edmonton')).strftime('%b %d, %I:%M %p %Z')
            try:
                nonce = str(int(agent['failure'] * 1000)) + '-' + name + '-' + notice[:1]
                message_id = sender(cfg, (prefix + '\n' if prefix else '') + text, nonce[:25])
                acknowledge(agent, notice)
                count += 1
                print(json.dumps({'agent': name, 'notice': notice, 'message_id': message_id}))
            except Exception as exc:
                # Keep unacknowledged incident for next minute; never print server bodies/secrets.
                print(json.dumps({'agent': name, 'delivery_error': type(exc).__name__}), file=sys.stderr)
    state['cursor'] = now
    if probe:
        state['last_probe'] = now
    state['last_completed'] = now
    print(json.dumps({'host': cfg['host'], 'checked': len(cfg['agents']), 'notices': count}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--collect')
    parser.add_argument('--since', type=float, default=0)
    parser.add_argument('--probe', action='store_true')
    parser.add_argument('--config')
    args = parser.parse_args()
    if args.collect:
        try:
            print(json.dumps(collect(args.collect, args.since, args.probe)))
        except MonitoringReadError as exc:
            print('MONITOR_READ_ERROR: ' + str(exc), file=sys.stderr)
            sys.exit(1)
        return
    import fcntl
    config_path = Path(args.config)
    os.umask(0o077)
    with open(config_path.with_suffix('.lock'), 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        cfg = json.loads(config_path.read_text())
        path = config_path.with_suffix('.state.json')
        state = json.loads(path.read_text()) if path.exists() else {}
        run(cfg, state)
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(state))
        temp.replace(path)


if __name__ == '__main__':
    main()
