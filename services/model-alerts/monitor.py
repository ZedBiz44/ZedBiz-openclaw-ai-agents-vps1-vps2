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


def read_db(path):
    return sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True, timeout=10)


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
        for raw, created in db.execute(
            'SELECT event_json,created_at FROM transcript_events WHERE created_at>=?',
            (int(since * 1000),),
        ):
            event = json.loads(raw)
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


def log_events(lines, primary, since):
    events = []
    for line in lines.splitlines():
        stamp = re.search(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d))', line)
        if not stamp:
            continue
        when = dt.datetime.fromisoformat(stamp[1].replace('Z', '+00:00')).timestamp()
        if when <= since:
            continue
        fields = dict(re.findall(r'(requested|candidate|decision|reason)=([^\s]+)', line))
        if fields.get('requested') != primary:
            continue
        if fields.get('decision') == 'candidate_failed' and fields.get('candidate') == primary:
            reason = 'Primary model request failed'
            lower = line.lower()
            if 'auth' in lower or 'token_revoked' in lower:
                reason = 'Codex sign-in rejected; reconnection may be required'
            elif 'rate' in lower or '429' in lower:
                reason = 'Primary model rate limit reached'
            events.append((when, 'failure', reason))
        elif fields.get('decision') == 'candidate_succeeded':
            if fields.get('candidate') == primary:
                events.append((when, 'success', ''))
            else:
                events.append((when, 'fallback', fields.get('candidate', 'backup model')))
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
                state.setdefault('reason', 'Primary model unavailable; backup answered')
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
        state.clear()


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
    source = Path(__file__).read_text()
    last = state.get('cursor', now - 60)
    # Replay a short overlap, with timestamp filtering; cap catch-up after long downtime.
    since = max(last, now - 3600)
    probe = now - state.get('last_probe', 0) >= 300
    count = 0
    for name, root in cfg['agents'].items():
        agent = state.setdefault('agents', {}).setdefault(name, {})
        try:
            if cfg['mode'] == 'docker':
                raw = subprocess.run(['docker', 'exec', '-i', name, 'python3', '-', '--collect', root,
                                      '--since', str(since), *(['--probe'] if probe else [])],
                                     input=source, text=True, capture_output=True, timeout=30, check=True)
                logs = subprocess.run(['docker', 'logs', '--timestamps', '--since', str(since), name],
                                      text=True, capture_output=True, timeout=15, check=True)
            else:
                active = subprocess.run(['systemctl', 'is-active', 'openclaw-' + name], capture_output=True)
                if active.returncode:
                    raise RuntimeError('service unavailable')
                raw = subprocess.run([sys.executable, __file__, '--collect', root, '--since', str(since),
                                      *(['--probe'] if probe else [])],
                                     text=True, capture_output=True, timeout=30, check=True)
                logs = subprocess.run(['journalctl', '-u', 'openclaw-' + name, '--since', '@' + str(int(since)),
                                       '--no-pager', '-o', 'cat'], text=True, capture_output=True, timeout=15, check=True)
            observation = json.loads(raw.stdout)
            primary = observation['primary']
            events = log_events(logs.stdout + '\n' + logs.stderr, primary, last)
            if observation['success']:
                events.append((observation['success'], 'success', ''))
            if observation['oauth'] == 'revoked':
                events.append((now, 'failure', 'Codex OAuth credential revoked; sign in again'))
            # Authentication acceptance alone does NOT establish successful model recovery.
            agent['primary'] = primary
            agent.pop('collection_error', None)
        except Exception as exc:
            agent['collection_error'] = type(exc).__name__
            events = [(now, 'failure', 'Agent service or monitoring read unavailable; needs checking')]
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
        print(json.dumps(collect(args.collect, args.since, args.probe)))
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
