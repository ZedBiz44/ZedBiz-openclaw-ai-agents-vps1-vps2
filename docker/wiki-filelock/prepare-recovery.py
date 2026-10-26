"""Create a complete local image archive before any live deployment."""
import hashlib,json,os,pathlib,shutil,subprocess
P=pathlib.Path;SRC=P('/tmp/cody-wiki-filelock-20261026');ROOT=P('/opt/openclaw/recovery/wiki-filelock-20261026');os.umask(0o077)
assert all(json.loads((SRC/'test-proof.json').read_text()).values()) and json.loads((SRC/'wiki-proof.json').read_text())['passed']
assert json.loads((SRC/'gate-proof.json').read_text())['passed']
assert shutil.disk_usage('/opt').free>45*1024**3
ROOT.mkdir(mode=0o755);os.chmod(ROOT,0o755)
for p in SRC.iterdir():
 if p.is_file() and (p.suffix in ['.py','.mjs'] or p.name in ['Dockerfile','inventory.json','images.json','test-proof.json','wiki-proof.json','gate-proof.json']):shutil.copy2(p,ROOT/p.name)
images=json.loads((ROOT/'images.json').read_text());inventory=json.loads((ROOT/'inventory.json').read_text());catalog=[]
for row in images:catalog.append({'id':row['id'],'refs':[row['after']],'roles':['gateway']})
for row in inventory:
 for image in row['images']:
  if image['ref']!=row['imageRef'] and not any(i['id']==image['id'] for i in catalog):catalog.append({'id':image['id'],'refs':[image['ref']],'roles':['asana']})
assert len(images)==11 and len(catalog)==13
archive=ROOT/'images.tar.gz'
with archive.open('xb') as out,(ROOT/'save.private.log').open('w') as err:
 save=subprocess.Popen(['docker','save',*[r for i in catalog for r in i['refs']]],stdout=subprocess.PIPE,stderr=err)
 compress=subprocess.Popen(['nice','-n','15','pigz','-p','2','-3'],stdin=save.stdout,stdout=out,stderr=err);save.stdout.close()
 assert compress.wait(timeout=1800)==0 and save.wait(timeout=60)==0
assert subprocess.run(['pigz','-t',str(archive)]).returncode==0
with archive.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
os.chmod(archive,0o644)
(ROOT/'archive.json').write_text(json.dumps({'archive':str(archive),'sha256':digest},indent=2))
(ROOT/'catalog.json').write_text(json.dumps({'images':catalog,'archiveBytes':archive.stat().st_size,'archiveSha256':digest},indent=2))
print(json.dumps({'recoveryArchiveCreated':True,'images':len(catalog),'bytes':archive.stat().st_size,'sha256':digest}),flush=True)
