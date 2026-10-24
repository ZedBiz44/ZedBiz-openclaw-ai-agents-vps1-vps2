#!/usr/bin/env python3
"""Apply a reversible routing note or run one fresh read-only agent search test."""
import concurrent.futures, hashlib, json, os, pathlib, re, subprocess, sys

kind, action, *names = sys.argv[1:]
allowed = {'vps1': {'terry','edith','amanda','marsha','maggie','inga','gohzed','grogar','wilma','victor','vivian'}, 'vps2': {'harry','suzy','frank'}}
assert kind in allowed and action in {'apply','test'} and names and set(names) <= allowed[kind]
base = pathlib.Path('/home/jackadmin/openclaw-backups/notion-search-20260912' if kind == 'vps1' else '/root/openclaw-fleet94-20260912/notion-search-repair')
base.mkdir(mode=0o700, parents=True, exist_ok=True)
note = (pathlib.Path(__file__).parent/'notion-search-route-note.md').read_bytes().replace(b'\r\n', b'\n').strip()
heading = b'## Notion Search Routing'

def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, **kwargs)

def apply(n):
    b = base/n; b.mkdir(mode=0o700, exist_ok=True)
    target = '/home/node/.openclaw/workspace/AGENTS.md' if kind == 'vps1' else '/root/.openclaw-'+n+'/workspace/AGENTS.md'
    old = run(['docker','exec',n,'cat',target]).stdout if kind == 'vps1' else pathlib.Path(target).read_bytes()
    if heading in old:
        assert note in old.replace(b'\r\n',b'\n'), 'Existing routing note differs; inspect before editing'
        return {'agent':n,'status':'already matches'}
    title = re.search(br'(?m)^(?:\xef\xbb\xbf)?# [^\r\n]+\r?\n', old)
    assert title, 'No Markdown title found; inspect before editing'
    backup = b/'AGENTS.md.before'; assert not backup.exists(), 'Previous attempt exists; inspect first'
    backup.write_bytes(old); backup.chmod(0o600)
    newline = b'\r\n' if b'\r\n' in old else b'\n'
    offset = title.end()
    inserted = newline+note.replace(b'\n',newline)+newline+newline
    new = old[:offset]+inserted+old[offset:]
    assert new[:offset]+new[offset+len(inserted):] == old
    if kind == 'vps1':
        script = "const fs=require('fs');const p=process.argv[1],t=p+'.notion-search.tmp',s=fs.statSync(p);if(fs.existsSync(t))throw Error('temporary file exists');fs.writeFileSync(t,fs.readFileSync(0),{flag:'wx',mode:s.mode&511});fs.chownSync(t,s.uid,s.gid);fs.renameSync(t,p);"
        run(['docker','exec','-i','--user','0',n,'node','-e',script,target],input=new)
        actual = run(['docker','exec',n,'cat',target]).stdout
    else:
        p=pathlib.Path(target); st=p.stat(); tmp=p.with_name(p.name+'.notion-search.tmp')
        with tmp.open('xb') as out: out.write(new)
        os.chmod(tmp,st.st_mode & 0o777); os.chown(tmp,st.st_uid,st.st_gid); tmp.replace(p)
        actual=p.read_bytes()
    assert actual == new
    result={'agent':n,'status':'applied','originalSha256':hashlib.sha256(old).hexdigest(),'updatedSha256':hashlib.sha256(new).hexdigest(),'onlyRoutingNoteAdded':True,'backup':str(backup)}
    (b/'instruction-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def test(n):
    b=base/n; b.mkdir(mode=0o700,exist_ok=True)
    msg='Jack asks: find the Notion documents about our OpenClaw update procedures, then open one relevant result. Use your current operating instructions and existing authorized Notion connection. This is a read-only acceptance test: do not change settings or content, contact anyone or resume assignments. Report the exact search tool, response type, result count and the ID of the page you opened; do not report private page contents.'
    args=['agent','--agent','main','--session-key','agent:main:notion-search-acceptance-'+n+'-20260912','--message',msg,'--timeout','240','--json']
    env=None
    if kind=='vps1': cmd=['docker','exec',n,'openclaw']+args
    else:
        s=pathlib.Path('/root/.openclaw-'+n);env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=(s/'.op.token').read_text().strip()
        env.update(HOME=str(s),OPENCLAW_STATE_DIR=str(s),OPENCLAW_CONFIG_PATH=str(s/'openclaw.json'),NODE_OPTIONS='--max-old-space-size=1536')
        cmd=['op','run','--env-file='+str(s/'.env'),'--','/opt/openclaw-'+n+'/node_modules/.bin/openclaw']+args
    r=subprocess.run(cmd,env=env,text=True,capture_output=True)
    (b/'fresh-agent-search.json').write_text(r.stdout+r.stderr)
    assert r.returncode==0, 'Inspect private fresh-agent-search log for '+n
    j=json.JSONDecoder().raw_decode(r.stdout[r.stdout.index('{'):])[0]
    payloads=[p.get('text','') for p in j.get('result',j).get('payloads',[])]
    return {'agent':n,'payloads':payloads}

if action=='apply':
    for n in names: print(json.dumps(apply(n)),flush=True)
else:
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        jobs={pool.submit(test,n):n for n in names}
        for future in concurrent.futures.as_completed(jobs):
            print(json.dumps(future.result()),flush=True)
