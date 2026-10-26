"""Build each customized cohort from its verified previous image; no live changes."""
import json,pathlib,shutil,subprocess
root=pathlib.Path('/opt/openclaw/backups/release-20261023');out=root/'cohort-builds';out.mkdir(exist_ok=True)
baseline={x['agent']:x for x in json.loads((root/'fleet-before.json').read_text())}
result=[]
for name in ['amanda','victor','wilma','grogar','maggie','marsha']:
 old=baseline[name]
 assert subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',old['image']],text=True).strip()==old['imageId']
 assert shutil.disk_usage('/opt').free>25*1024**3,'Retain rollback disk headroom'
 tag=f'zedbiz/{name}:2026.10.6-core-20261023'
 with (out/(name+'.log')).open('w') as log:
  subprocess.run(['docker','build','--network','host','--build-arg','BASE_IMAGE='+old['image'],'--build-arg','COHORT='+name,'-f','Dockerfile.cohort','-t',tag,'.'],cwd='/home/jackadmin/vps1-10-6-20261023',stdout=log,stderr=subprocess.STDOUT,check=True)
 image=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',tag],text=True).strip()
 item={'agent':name,'baseImage':old['imageId'],'ref':tag,'id':image,'buildChecksPassed':True}
 result.append(item);(out/'images.json').write_text(json.dumps(result,indent=2));print(json.dumps(item),flush=True)
