"""Read-only final verification of running artifacts, services and accepted releases."""
import datetime
import json
from pathlib import Path
import subprocess

agents = ['amanda','victor','wilma','vivian','inga','maggie','gohzed','grogar','edith','terry','marsha']
results = []
for name in agents:
    recovery = Path('/opt/openclaw/recovery')/(name+'-20261018') if name in {'amanda','victor'} else Path('/opt/openclaw/recovery/fleet-20261018')/name
    manifest = json.loads((recovery/'manifest.json').read_text())
    identities = {x['ref']:x['id'] for x in manifest['images'] if x['automatic']}
    containers = []
    for container in [name, name+'-asana-mcp']:
        obj = json.loads(subprocess.check_output(['docker','inspect',container],text=True))[0]
        containers.append(dict(name=container,id=obj['Id'],image=obj['Image'],ref=obj['Config']['Image'],
            imageMatchesManifest=identities.get(obj['Config']['Image'])==obj['Image'],
            health=obj['State'].get('Health',{}).get('Status'),restarts=obj['RestartCount'],oom=obj['State']['OOMKilled']))
    raw = subprocess.check_output(['systemctl','show','openclaw-'+name+'.service',
        '-p','ActiveState','-p','SubState','-p','Result','-p','UnitFileState'],text=True)
    service = dict(line.split('=',1) for line in raw.splitlines() if '=' in line)
    config = json.loads((Path('/opt/openclaw/agents')/name/'config/openclaw.json').read_text())
    accepted = None
    receipt = Path('/opt/openclaw/backups/fleet-20261018')/name/'acceptance.json'
    if receipt.exists():
        a = json.loads(receipt.read_text())
        accepted = dict(accepted=a['accepted'],sameContainer=a['containerId']==containers[0]['id'],
            cronCount=a['cronCount'],runId=a['receipt']['runId'])
    version = subprocess.check_output(['docker','exec','-u','node',name,'node','/app/openclaw.mjs','--version'],text=True,timeout=60).strip()
    assert '2026.10.4' in version
    assert all(c['imageMatchesManifest'] and c['health']=='healthy' and not c['oom'] and c['restarts']==0 for c in containers)
    assert service=={'Result':'success','ActiveState':'active','SubState':'exited','UnitFileState':'enabled'}
    if name not in {'amanda','victor'}:
        assert accepted and accepted['accepted'] and accepted['sameContainer']
    results.append(dict(agent=name,version=version,service=service,containers=containers,
        idleCleanupMs=config.get('mcp',{}).get('sessionIdleTtlMs'),acceptance=accepted))
print(json.dumps(dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),allPassed=True,agents=results)),flush=True)

