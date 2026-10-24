"""Offline recovery point and isolated restored state; never substitutes live state."""
import hashlib,json,os,pathlib,shutil,sqlite3,subprocess,sys,time
os.umask(0o077)
name,action=sys.argv[1:3]
assert name=='terry','Pilot only until acceptance'
live=pathlib.Path('/opt/openclaw/agents')/name
work=pathlib.Path('/opt/openclaw/backups/release-20261023')/name
stage=work/'rehearsal'
image='zedbiz/openclaw-base:2026.10.6-core-20261023'
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rpc(method,params=None):
 args=['docker','exec',name,'openclaw','gateway','call',method,'--json']
 if params:args+=['--params',json.dumps(params)]
 p=subprocess.run(args,capture_output=True,text=True)
 assert p.returncode==0,'RPC failed; no stop attempted'
 return json.JSONDecoder().raw_decode(p.stdout[p.stdout.index('{'):])[0]
if action=='backup':
 assert not stage.exists() and not (work/'state-before.tar.gz').exists(),'Existing backup must not be overwritten'
 assert shutil.disk_usage(work).free>20*1024**3
 active=rpc('status').get('shutdownBudget',{}).get('activeWork')
 assert active and all(x==0 for x in active.values()),'Active work; retry without interruption'
 cron=rpc('cron.list',{'includeDisabled':True})
 assert not any(j.get('state',{}).get('runningAtMs') for j in cron['jobs']),'Scheduled work active'
 d=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert d['State']['Health']['Status']=='healthy'
 (work/'mounts-before.json').write_text(json.dumps(d['Mounts'],indent=2))
 (work/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n')
 (work/'cron-checkpoint.json').write_text(json.dumps(cron,indent=2))
 manifest=pathlib.Path('/opt/openclaw/recovery/fleet-20261018/terry/manifest.json')
 shutil.copy2(manifest,work/'manifest-before.json')
 shutil.copy2(live/'docker-compose.yml',work/'compose-before.yml')
 (work/'image-before.json').write_text(json.dumps({'ref':d['Config']['Image'],'id':d['Image']}))
 archive=work/'state-before.tar.gz'
 try:
  with (work/'checkpoint-stop.log').open('w') as out:subprocess.run(['systemctl','stop','openclaw-'+name+'.service'],stdout=out,stderr=subprocess.STDOUT,check=True)
  assert subprocess.run(['docker','inspect',name],capture_output=True).returncode!=0
  subprocess.run(['nice','-n','15','tar','-I','pigz -p 2 -3','-cf',str(archive),'-C',str(live),'.'],check=True)
  subprocess.run(['tar','-tf',str(archive)],stdout=subprocess.DEVNULL,check=True)
 finally:
  with (work/'checkpoint-restart.log').open('w') as out:subprocess.run(['systemctl','start','openclaw-'+name+'.service'],stdout=out,stderr=subprocess.STDOUT,check=True)
 stage.mkdir(mode=0o700)
 subprocess.run(['tar','-xf',str(archive),'-C',str(stage)],check=True)
 checked=[]
 for p in [stage/'config/state/openclaw.sqlite',*(stage/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  if p.exists():
   with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
    db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True)
    assert db.execute('pragma quick_check').fetchall()==[('ok',)],'Invalid restored database'
   checked.append(str(p.relative_to(stage)))
 assert checked
 result={'archive':str(archive),'sha256':sha(archive),'restoredDatabases':checked,'originalImage':d['Image'],'stage':str(stage)}
 (work/'checkpoint.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
elif action=='prepare-mem0':
 assert (work/'checkpoint.json').exists()
 target=stage/'config/scripts/repair-mem0-host-peer.mjs'
 assert target.is_file() and '2026.10.6' not in target.read_text()
 shutil.copy2(target,work/'mem0-peer-before.mjs')
 s=target.stat();target.write_bytes(pathlib.Path('/home/jackadmin/vps1-10-6-20261023/repair-mem0-host-peer.mjs').read_bytes());os.chown(target,s.st_uid,s.st_gid)
 print(json.dumps({'preparedMem0Guard':True,'scope':'restored copy'}),flush=True)
elif action in ['lint','migrate','plugins','mem0','models','model-probe']:
 assert (work/'checkpoint.json').exists()
 args=['docker','run','--rm','--network','mem0-dev_mem0_network','--network','openclaw','--memory','3g','--env-file',str(work/'runtime.env'),'--user','node','--entrypoint','node']
 for m in json.loads((work/'mounts-before.json').read_text()):
  src=m['Source'];dst=m['Destination']
  if src.startswith(str(live)+'/'):src=str(stage/src[len(str(live))+1:])
  elif src=='/var/run/docker.sock':continue
  elif src=='/dev/shm':continue
  else:
   args+=['-v',src+':'+dst+':ro'];continue
  args+=['-v',src+':'+dst+('' if m['RW'] else ':ro')]
 command={'lint':['doctor','--lint','--json'],'migrate':['doctor','--fix','--non-interactive'],'plugins':['plugins','list','--json'],'mem0':[],
 'models':['models','status','--json'],
 'model-probe':['agent','--local','--agent','main','--session-id','cody-10-6-restored-model-proof','--message','Read-only upgrade rehearsal. Reply exactly MODEL_OK. Do not call tools, modify files, send messages, or delegate.','--json']}[action]
 if action=='mem0':
  args[args.index('--entrypoint')+1]='sh'
  args+=[image,'/home/node/.openclaw/workspace/ensure-mem0-compat.sh']
 else:args+=[image,'/app/openclaw.mjs',*command]
 log=work/('rehearsal-'+action+'-'+str(int(time.time()))+'.log')
 with log.open('w') as out:p=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT)
 receipt={'phase':action,'exit':p.returncode,'privateLog':str(log)}
 (work/('rehearsal-'+action+'-receipt.json')).write_text(json.dumps(receipt,indent=2))
 print(json.dumps(receipt),flush=True)
 sys.exit(p.returncode)
else:raise SystemExit('Unsupported stage')
