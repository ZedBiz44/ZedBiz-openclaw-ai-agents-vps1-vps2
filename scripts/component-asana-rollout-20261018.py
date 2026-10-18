"""One idle agent's Asana sidecar; preserve catalog, identity, and recovery image IDs."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
os.umask(0o077)
name=sys.argv[1]
assert name in {'wilma','vivian','inga','maggie','gohzed','grogar','terry','edith','marsha','amanda','victor'}
live=Path('/opt/openclaw/agents')/name
work=Path('/opt/openclaw/backups/components-20261018')/name
catalog=json.loads(Path('/opt/openclaw/recovery/components-asana-20261018/catalog.json').read_text())
proof=json.loads(Path('/opt/openclaw/recovery/components-asana-20261018/archive-proof.json').read_text())
assert proof['allImageIdsVerified'] and proof['archiveSha256']==catalog['sha256']
assert (work/'acceptance.json').exists(), 'Gateway acceptance must finish first'
r=subprocess.run(['docker','exec','-u','node',name,'node','/app/openclaw.mjs','gateway','call','status','--json'],capture_output=True,text=True,timeout=120)
assert r.returncode==0
active=json.loads(r.stdout[r.stdout.index('{'):]).get('shutdownBudget',{}).get('activeWork')
assert active and all(v==0 for v in active.values()), 'Agent busy; retry after work completes'
container=name+'-asana-mcp'
d=json.loads(subprocess.check_output(['docker','inspect',container],text=True))[0]
old=d['Config']['Image'];new='zedbiz/asana-http-mcp:2.0.0-'+('edith-' if name=='edith' else '')+'components-20261018'
assert old!=new, 'Already activated; verify existing receipt'
js="""import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StreamableHTTPClientTransport} from '@modelcontextprotocol/sdk/client/streamableHttp.js';
const c=new Client({name:'cody-readonly-maintenance',version:'1.0'});
await c.connect(new StreamableHTTPClientTransport(new URL('http://127.0.0.1:8080/mcp'),{requestInit:{headers:{Authorization:'Bearer '+process.env.MCP_AUTH_TOKEN}}}));
console.log(JSON.stringify({tools:(await c.listTools()).tools.map(t=>t.name).sort(),identity:await c.callTool({name:'asana_get_user',arguments:{user_gid:'me'}})}));await c.close();"""
def probe(label):
    p=subprocess.run(['docker','exec',container,'node','--input-type=module','-e',js],capture_output=True,text=True,timeout=120)
    (work/('asana-'+label+'.log')).write_text(p.stdout+p.stderr)
    assert p.returncode==0, 'Inspect protected Asana probe log'
    obj=json.loads(p.stdout)
    assert not obj['identity'].get('isError')
    return obj
before=probe('before')
manifest=Path('/opt/openclaw/recovery')/(name+'-20261018')/'manifest.json' if name in {'amanda','victor'} else Path('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json'
shutil.copy2(live/'docker-compose.yml',work/'compose-before-asana.yml');shutil.copy2(manifest,work/'manifest-before-asana.json')
s=(live/'docker-compose.yml').read_text();assert s.count(old)==1
(live/'docker-compose.yml').write_text(s.replace(old,new))
refs=subprocess.check_output(['docker','compose','--env-file','.env','config','--images'],cwd=live,text=True).split()
ids={x['ref']:x['id'] for x in catalog['images']};assert set(refs)<=ids.keys()
m=json.loads(manifest.read_text());m.update(archive=catalog['archive'],sha256=catalog['sha256'],images=[{'ref':r,'id':ids[r],'automatic':True} for r in sorted(set(refs))]);manifest.write_text(json.dumps(m,indent=2))
env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=(live/'.op.token').read_text().strip()
with (work/'asana-activation.log').open('w') as out:
    subprocess.run(['op','run','--env-file','.env','--','docker','compose','up','-d','--no-deps',d['Config']['Labels']['com.docker.compose.service']],cwd=live,env=env,stdout=out,stderr=subprocess.STDOUT,check=True,timeout=180)
for _ in range(30):
    d=json.loads(subprocess.check_output(['docker','inspect',container],text=True))[0]
    if d['State'].get('Health',{}).get('Status')=='healthy':break
    time.sleep(3)
else:raise RuntimeError('Asana health deadline')
assert d['Image']==ids[new] and d['RestartCount']==0
after=probe('after');assert before==after, 'Asana catalog or identity changed'
result={'agent':name,'image':new,'id':d['Image'],'catalogCount':len(after['tools']),'catalogAndIdentityPreserved':True}
(work/'asana-acceptance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
