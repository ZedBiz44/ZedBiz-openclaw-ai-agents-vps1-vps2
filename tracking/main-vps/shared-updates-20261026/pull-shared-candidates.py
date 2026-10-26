"""Fetch only the approved version tags and record immutable image identities."""
import subprocess,json,pathlib,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');targets={'qdrant':'qdrant/qdrant:v1.20.0','connect-api':'1password/connect-api:1.8.4','connect-sync':'1password/connect-sync:1.8.4','portainer':'portainer/portainer-ce:2.45.3','uptime-kuma':'louislam/uptime-kuma:2.5.7','dozzle':'amir20/dozzle:v11.3.4','homepage':'ghcr.io/gethomepage/homepage:v2.7.0'};catalog={}
for name,ref in targets.items():
 with (W/(name+'-pull.private.log')).open('w') as out:p=subprocess.run(['docker','pull',ref],stdout=out,stderr=subprocess.STDOUT,timeout=900)
 assert p.returncode==0,'Candidate pull failed: '+name
 d=json.loads(subprocess.check_output(['docker','image','inspect',ref]))[0];assert d['Architecture']=='amd64' and d['RepoDigests'];catalog[name]={'tag':ref,'imageId':d['Id'],'pinnedRef':d['RepoDigests'][0],'versionLabels':{k:v for k,v in (d['Config'].get('Labels') or {}).items() if k.endswith(('image.version','image.revision'))}};(W/'candidate-images.json').write_text(json.dumps(catalog,indent=2));print(json.dumps({'candidate':name,**catalog[name]}),flush=True)
