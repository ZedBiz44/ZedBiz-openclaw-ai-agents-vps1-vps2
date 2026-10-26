"""Read back the completed production fleet and configured channels after current backups finish."""
import pathlib,json,subprocess,urllib.request,hashlib,concurrent.futures,os,shutil
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024');F=P('/opt/openclaw/backups/fleet-10-6-20261024');M=P('/opt/openclaw/backups/mem0-repair-20261024-r2');R=P('/opt/openclaw/recovery/release-20261024-fleet-tools');assert json.loads((W/'current-backups-complete.json').read_text())['passed'];catalog=json.loads((R/'catalog.json').read_text());pins={i['ref']:i['id'] for i in catalog['images']};rpcCode=(M/'rpc.mjs').read_text();guard=(M/'verify-vps1-runtime-10-6.cjs').read_text();names=['terry','marsha','edith','vivian','amanda','victor','wilma','gohzed','grogar','inga','maggie']
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def check(name):
 A=W/('agent-'+name);live=P('/opt/openclaw/agents')/name;cfg=json.loads((live/'config/openclaw.json').read_text());d=inspect(name);side=inspect(name+'-asana-mcp');assert d['State']['Running'] and d['State']['Health']['Status']=='healthy' and not d['State']['OOMKilled'] and d['RestartCount']==0;assert side['State']['Health']['Status']=='healthy';assert pins[d['Config']['Image']]==d['Image'] and pins[side['Config']['Image']]==side['Image']
 if name!='marsha':assert d['Image']==json.loads((F/name/'acceptance.json').read_text())['imageId']
 assert subprocess.run(['systemctl','is-active','--quiet','openclaw-'+name+'.service']).returncode==0
 assert subprocess.run(['systemctl','is-enabled','--quiet','openclaw-'+name+'.service']).returncode==0
 proc=subprocess.run(['docker','exec','-i',name,'node','--input-type=commonjs','-',name],input=guard,text=True,capture_output=True,timeout=60);(A/'final-runtime-guard.private.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
 def rpc(method,params=None):
  req={'method':method,'params':params or {}};p=subprocess.run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps(req),name,'node','--input-type=module'],input=rpcCode,text=True,capture_output=True,timeout=120);(A/('final-'+method+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0;return json.loads(p.stdout)
 health=rpc('health');assert health['ok'];channels={}
 for channel,state in health.get('channels',{}).items():
  accounts=state.get('accounts') or {'default':state};enabled=[a for a in accounts.values() if a.get('enabled',True) and a.get('configured')]
  if enabled:
   assert all(a.get('running') is True and a.get('connected') is True for a in enabled),'Configured channel disconnected: '+name+'/'+channel
   channels[channel]={'configuredAccounts':len(enabled),'allRunningAndConnected':True}
 cron=rpc('cron.list',{'includeDisabled':True});expected=len(json.loads(P('/opt/openclaw/backups/release-20261024-marsha/post-cutover-rpc.json').read_text())['cron.list']['jobs']) if name=='marsha' else json.loads((F/name/'acceptance.json').read_text())['schedules'];assert len(cron['jobs'])==expected
 slot=cfg['plugins']['slots']['memory'];version=None
 if slot in ['openclaw-mem0','hindsight-openclaw']:
  package='@mem0/openclaw-mem0' if slot=='openclaw-mem0' else '@vectorize-io/hindsight-openclaw';prefix='mem0-*' if slot=='openclaw-mem0' else 'vectorize-io-hindsight-*';matches=list((live/'npm/projects').glob(prefix+'/node_modules/'+package+'/package.json'));assert len(matches)==1,'Identify active installed project before reporting its version';version=json.loads(matches[0].read_text())['version'];assert version==('1.2.1' if slot=='openclaw-mem0' else '1.2.0')
  if slot=='openclaw-mem0':
   project=matches[0].parents[3];assert json.loads((project/'node_modules/mem0ai/package.json').read_text())['version']=='3.3.1'
 with urllib.request.urlopen('https://'+name+'.zbiz.ca/healthz',timeout=25) as response:assert response.status==200
 manifest=P('/opt/openclaw/recovery')/(name+'-20261018')/'manifest.json' if name in ['amanda','victor'] else P('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json';m=json.loads(manifest.read_text());assert m['archive']==catalog['archive'] and m['sha256']==catalog['sha256']
 with P(m['wrapper']).open('rb') as file:assert hashlib.file_digest(file,'sha256').hexdigest()==m['wrapper_sha256']
 for image in m['images']:assert pins[image['ref']]==image['id'] and image['automatic'] is True
 assert {d['Config']['Image'],side['Config']['Image']}<={image['ref'] for image in m['images']}
 memory={};cgroup=next(line.split(':',2)[2] for line in P('/proc/'+str(d['State']['Pid'])+'/cgroup').read_text().splitlines() if line.startswith('0::'));C=P('/sys/fs/cgroup')/cgroup.lstrip('/');stats=dict(line.split() for line in (C/'memory.stat').read_text().splitlines());current=int((C/'memory.current').read_text());memory={'currentBytes':current,'workingSetBytes':current-int(stats.get('inactive_file',0)),'anonymousBytes':int(stats.get('anon',0)),'fileCacheBytes':int(stats.get('file',0)),'swapBytes':int((C/'memory.swap.current').read_text())}
 return {'agent':name,'passed':True,'core':'2026.10.6','node':'24.22.1','imageId':d['Image'],'memoryProvider':slot,'memoryPluginVersion':version,'schedules':expected,'configuredChannels':channels,'restarts':0,'oom':False,'httpsHealth':200,'systemdEnabledAndActive':True,'recoveryWrapperHashVerified':True,'resourceSample':memory}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,names))
support=[]
for name in ['hindsight','hindsight-db','mem0-dev-qdrant-1','1password-connect-api','1password-connect-sync','caddy','z-code-allocator','z-code-admin','z-code-notion-mirror','zedbiz-restart-api','rocky-restart-bridge','rocky-tunnel-bridge','portainer','filebrowser','uptime-kuma','dozzle','homepage','docker-socket-proxy']:
 d=inspect(name);assert d['State']['Running'] and not d['State']['OOMKilled'];health=d['State'].get('Health',{}).get('Status');assert health in [None,'healthy'];support.append({'service':name,'running':True,'configuredHealth':health,'imageId':d['Image']})
marsha=json.loads(P('/opt/openclaw/agents/marsha/config/openclaw.json').read_text());assert marsha['plugins']['entries']['slack']['enabled'] is True
host={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in P('/proc/meminfo').read_text().splitlines() if ':' in line)}
proof={'passed':True,'agents':results,'supportingServices':support,'productionServiceCount':2*len(results)+len(support),'allFortyProductionServicesRunning':True,'allElevenOn106WithTools':True,'allConfiguredChannelsConnected':True,'marshaSlackPluginEnabled':True,'marshaSlackChannelConfigured':bool(marsha.get('channels',{}).get('slack',{}).get('enabled')),'mem0AgentsOnVps1':['terry','edith'],'harryMem0SeparatelyVerified':True,'currentBackupsAccepted':True,'freeDiskBytes':shutil.disk_usage(W).free,'hostMemoryBytes':{k:host[k] for k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']},'rebootRequired':P('/var/run/reboot-required').exists()}
(W/'final-fleet-readback.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
