"""Build tiny layers atop exact inventoried gateway images; never recreate services."""
import hashlib,json,pathlib,subprocess
P=pathlib.Path;ROOT=P(__file__).resolve().parent
inventory=json.loads((ROOT/'inventory.json').read_text());built=[]
for row in inventory:
 agent=row['agent'];base=row['imageRef'];ref='zedbiz/'+agent+':2026.10.6-wiki-filelock-20261026'
 before=json.loads(subprocess.check_output(['docker','image','inspect',base]))[0]
 assert before['Id']==row['image'],'Base image changed'
 # Digest-qualified local reference also guards against tag changes during build.
 with (ROOT/(agent+'-build.log')).open('w') as log:
  result=subprocess.run(['docker','build','--network','none','--build-arg','BASE_IMAGE='+base+'@'+row['image'],'-t',ref,str(ROOT)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
 assert result.returncode==0,agent+' build failed'
 after=json.loads(subprocess.check_output(['docker','image','inspect',ref]))[0]
 for key in ['Env','Entrypoint','Cmd','User','WorkingDir','Healthcheck','ExposedPorts']:
  assert before['Config'].get(key)==after['Config'].get(key),(agent,key)
 assert after['RootFS']['Layers'][:len(before['RootFS']['Layers'])]==before['RootFS']['Layers']
 result=subprocess.run(['docker','run','--rm','--network','none','--entrypoint','python3',ref,'-I','-B','/opt/zedbiz/wiki-lock/verify.py'],capture_output=True,text=True,timeout=30)
 assert result.returncode==0,agent+' gate failed'
 built.append({'agent':agent,'before':base,'baseId':row['image'],'after':ref,'id':after['Id'],'baseLayersAndRuntimeConfigPreserved':True})
 (ROOT/'images.json').write_text(json.dumps(built,indent=2));print(agent+' image verified',flush=True)
