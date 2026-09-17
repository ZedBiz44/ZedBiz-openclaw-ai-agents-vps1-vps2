#!/usr/bin/env python3
"""Bounded coordinator work outside email intake; scoped to the Edith project."""
import fcntl, json, os, re, signal, subprocess, sys, time, urllib.request
from pathlib import Path
from datetime import datetime, timezone

PROJECT = '1218559074752632'
AMANDA = '1213974002925107'
ROOT = Path('/home/node/.openclaw/private/amanda-edith-coordination')
ROOT.mkdir(mode=0o700, exist_ok=True)
cfg = json.loads(Path('/home/node/.openclaw/openclaw.json').read_text())['mcp']['servers']['asana']
headers = {'Content-Type':'application/json', 'Accept':'application/json, text/event-stream',
           **{k:os.path.expandvars(v) for k,v in cfg.get('headers',{}).items()}}


def rpc(method, params):
    req = urllib.request.Request(cfg['url'], data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        if response.headers.get('Mcp-Session-Id'): headers['Mcp-Session-Id'] = response.headers['Mcp-Session-Id']
        raw = response.read().decode()
    if 'event:' in raw or raw.startswith('data:'): raw = next(x[5:].strip() for x in raw.splitlines() if x.startswith('data:'))
    data = json.loads(raw)
    if 'error' in data: raise RuntimeError('Asana MCP protocol error')
    return data['result']


def call(name, args):
    r = rpc('tools/call', {'name':name, 'arguments':args})
    if r.get('isError'): raise RuntimeError('Asana MCP tool error: '+name)
    return json.loads(next(x['text'] for x in r['content'] if x['type']=='text'))


def save(gid, data):
    p = ROOT/(gid+'.json'); tmp = p.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2)); tmp.replace(p)


def dispatch(gid):
    assert re.fullmatch(r'\d{16}',gid)
    rpc('initialize', {'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'amanda-coordination','version':'1'}})
    me = call('asana_get_user', {'user_gid':'me'})
    assert me['gid']==AMANDA and me['email']=='amanda@zedworks.com'
    assert any(w['gid']=='11298561585567' for w in me['workspaces'])
    t = call('asana_get_task', {'task_id':gid,'opt_fields':'name,completed,assignee.gid,projects.gid,due_at,dependencies.gid'})
    assert any(p['gid']==PROJECT for p in t['projects']) and t['assignee']['gid']==AMANDA
    assert t['name'].startswith('Amanda') or t['name'].startswith('[Amanda exception]')
    if t['completed']: return {'status':'already-completed'}
    if t.get('due_at') and datetime.fromisoformat(t['due_at'].replace('Z','+00:00'))>datetime.now(timezone.utc): return {'status':'not-yet-due'}
    lock = (ROOT/'worker.lock').open('a')
    try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: return {'status':'worker-already-running'}
    if (ROOT/(gid+'.json')).exists(): return {'status':'already-dispatched-inspect-receipt'}
    prompt = ('Jack authorized completing the Edith project recovery. You are Amanda, coordinator. This is a separate bounded session after email intake; use your own PAT MCP. Read z-asana-agent-control and live task '+gid+' including comments, then finish its existing authorized deliverable. Do not start another Edith worker, change credentials, close folder parents or approve Ruby reviews. Edith uses 20-minute scheduled sittings; Ruby owns pending native approvals. Shared handoff proof IDs 1H7XiYTxhbIa-OA-SacVj9sljMOP20GCz and 1dfDPQoUzCLWbjgYo_jPXPZSuA4FAEtLG are readable using gog drive get with account jack@zbiz.work; do not search environment secrets. Read live tasks and open shared evidence through your approved Google route. Do useful checks for at most 7 minutes, reserve 2 minutes to report findings, exact blockers/owners and read back completion of only this check. Save memory only after useful work and report memory failure separately. Keep standing task 1218562186316309 open. No polling schedule or infrastructure changes. If the task is already done, verify and stop.')
    (ROOT/(gid+'.prompt.txt')).write_text(prompt)
    record = {'task':gid,'status':'launching','started':datetime.now(timezone.utc).isoformat()}
    save(gid,record)
    log = (ROOT/(gid+'.log')).open('ab',buffering=0)
    p = subprocess.Popen([sys.executable,__file__,'run',gid,str(lock.fileno())],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True,pass_fds=(lock.fileno(),))
    record.update(status='launched',pid=p.pid);save(gid,record)
    return record


def run(gid, fd):
    lock = os.fdopen(int(fd),'a'); time.sleep(.3)
    p = subprocess.Popen(['openclaw','agent','--agent','main','--session-key','agent:main:edith-coordination-'+gid,'--message-file',str(ROOT/(gid+'.prompt.txt')),'--timeout','600','--json'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
    expired = False
    try: out,err = p.communicate(timeout=660)
    except subprocess.TimeoutExpired:
        expired=True
        try: os.killpg(p.pid,signal.SIGTERM)
        except ProcessLookupError: pass
        try: out,err=p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            try: os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            out,err=p.communicate(timeout=10)
    (ROOT/(gid+'.result.json')).write_text(out)
    record=json.loads((ROOT/(gid+'.json')).read_text())
    record.update(status='worker-timeout' if expired else 'worker-returned',exit_code=124 if expired else p.returncode,ended=datetime.now(timezone.utc).isoformat());save(gid,record)
    if err: print(err[-1200:])


if __name__=='__main__':
    if sys.argv[1]=='dispatch': print(json.dumps(dispatch(sys.argv[2])))
    elif sys.argv[1]=='run': run(sys.argv[2],sys.argv[3])
    else: raise ValueError('Unsupported command')

