"""Final read-only fleet and recovery audit. Run as root on VPS1."""
import hashlib
import json
import pathlib
import subprocess

ROOT=pathlib.Path('/opt/openclaw/recovery/wiki-lock-20261023')
images=json.loads((ROOT/'images.json').read_text())
rows=[]
js=r"""
const fs=require('fs');
const c=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json'));
const w=c.plugins.entries['memory-wiki'].config;
const s=fs.statSync(w.vault.path+'/.openclaw-wiki/zedbiz-mutation.flock');
const state={corpus:w.search.corpus,lockDevice:s.dev,lockInode:s.ino};
(async()=>{try{const r=await fetch('http://127.0.0.1:'+(c.gateway.port||18789)+'/readyz',{signal:AbortSignal.timeout(15000)});
console.log(JSON.stringify({...state,ready:r.status}));}catch(e){console.log(JSON.stringify({...state,ready:null,readinessError:e.message}));}})();
"""
for a,e in images.items():
    base=pathlib.Path('/opt/openclaw/agents')/a
    manifest=pathlib.Path('/opt/openclaw/recovery')/(a+'-20261018')/'manifest.json'
    if not manifest.exists():manifest=pathlib.Path('/opt/openclaw/recovery/fleet-20261018')/a/'manifest.json'
    d=json.loads(manifest.read_text())
    live=json.loads(subprocess.check_output(['docker','inspect',a]))[0]
    state=json.loads(subprocess.check_output(['docker','exec',a,'node','-e',js],timeout=25))
    row={'agent':a,'image':live['Config']['Image'],'imageCorrect':live['Config']['Image']==e['after'],
         'restartCount':live['RestartCount'],'health':live['State'].get('Health',{}).get('Status'),
         'startupGuard':'shared-wiki-upgrade-gate' in (base/'workspace/post-start.sh').read_text(),
         'wrapperHashValid':hashlib.sha256(pathlib.Path(d['wrapper']).read_bytes()).hexdigest()==d['wrapper_sha256'],
         'recoveryImageIdsValid':all(json.loads(subprocess.check_output(['docker','image','inspect',i['ref']]))[0]['Id']==i['id'] for i in d['images']),
         'archive':d['archive'],**state}
    rows.append(row)
    print(json.dumps(row),flush=True)
(ROOT/'audit-result.json').write_text(json.dumps(rows,indent=2)+'\n')
assert len({(r['lockDevice'],r['lockInode']) for r in rows})==1, 'Agents do not share one lock inode'
assert all(r['imageCorrect'] and r['startupGuard'] and r['wrapperHashValid'] and r['recoveryImageIdsValid'] and r['corpus']=='wiki' for r in rows)
print('All agents share one lock; image, startup, recovery and Wiki-only settings verified.',flush=True)
