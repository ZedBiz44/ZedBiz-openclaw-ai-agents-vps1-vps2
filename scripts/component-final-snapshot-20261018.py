"""Read-only simultaneous fleet state, run after individual acceptance."""
import concurrent.futures, json, subprocess, time, urllib.request
from pathlib import Path

base = Path('/opt/openclaw/backups/components-20261018')
names = ['wilma','vivian','inga','maggie','gohzed','grogar','terry','edith','marsha','amanda','victor']
assert len(json.loads((base/'final-fleet-acceptance.json').read_text())) == len(names)
rows = []
for name in names:
    d = json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
    sidecar = json.loads(subprocess.check_output(['docker','inspect',name+'-asana-mcp'],text=True))[0]
    for container in [d, sidecar]:
        assert container['State']['Running'] and container['State']['Health']['Status']=='healthy'
        assert container['RestartCount']==0 and not container['State']['OOMKilled']
    assert subprocess.check_output(['systemctl','show','openclaw-'+name,'-p','Result','--value'],text=True).strip()=='success'
    manifest_path = Path('/opt/openclaw/recovery')/(name+'-20261018')/'manifest.json' if name in {'amanda','victor'} else Path('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    identities = {i['ref']:i['id'] for i in manifest['images']}
    for container in [d, sidecar]:
        assert identities[container['Config']['Image']]==container['Image']
    pid=d['State']['Pid']
    rel=Path('/proc/'+str(pid)+'/cgroup').read_text().strip().split('::',1)[1]
    cg=Path('/sys/fs/cgroup')/rel.lstrip('/')
    stats=dict(line.split() for line in (cg/'memory.stat').read_text().splitlines())
    events=dict(line.split() for line in (cg/'memory.events').read_text().splitlines())
    assert int(events['oom'])==0 and int(events['oom_kill'])==0
    current=int((cg/'memory.current').read_text())
    rows.append({'agent':name,'gatewayHealthy':True,'asanaHealthy':True,'restartCount':0,'imageManifestMatches':True,'memoryCurrentBytes':current,'memoryMinusInactiveFileBytes':current-int(stats.get('inactive_file',0)),'memoryMax':(cg/'memory.max').read_text().strip(),'memoryEvents':events})
def check_route(name):
    with urllib.request.urlopen('https://'+name+'.zbiz.ca/healthz',timeout=15) as r:
        assert r.status==200
        return {'agent':name,'status':r.status}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    routes=list(pool.map(check_route,names))
activation=json.loads((base/'host/activation.json').read_text())
shared=[]
for name in activation['sharedRestarted']:
    d=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
    assert d['State']['Running'] and not d['State']['OOMKilled']
    health=d['State'].get('Health',{}).get('Status')
    assert health in [None,'healthy']
    shared.append({'name':name,'running':True,'health':health,'restarts':d['RestartCount']})
result={'measuredAtUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'agents':rows,'publicRoutes':routes,'sharedContainers':shared}
(base/'final-simultaneous-snapshot.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
