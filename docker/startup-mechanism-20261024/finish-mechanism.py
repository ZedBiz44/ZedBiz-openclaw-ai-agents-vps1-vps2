import pathlib,json,subprocess,re,hashlib,os
P=pathlib.Path;W=P('/opt/openclaw/backups/startup-mechanism-20261024');out={'comparisons':{},'micro':{},'live':{},'functionalProof':json.loads((W/'sdk-memory-proof.json').read_text())}
for k in ['full','mem0-full','marsha-slack']:
 d=json.loads((W/k/'tests.json').read_text());out['comparisons'][k]=d
 for x in d['tests']:
  p=W/k/x['agent']/(x['variant']+'.log');s=p.read_text();x['topPluginLoads']=sorted([{'phase':m[1],'plugin':m[2],'ms':float(m[3])} for m in re.finditer(r'\[plugin-load-profile\] phase=(\S+) plugin=(\S+) elapsedMs=([\d.]+)',s)],key=lambda x:-x['ms'])[:8];x['workerTimeout']='worker task timed out' in s;x['delayedHeartbeat']='liveness heartbeat delayed' in s;x['memoryRegistered']=('openclaw-mem0: registered' in s) if x['agent']=='terry' else bool(re.search(r'phase=full plugin=hindsight-openclaw ',s))
for v in ['stock','batch','fs026','fs026-batch']:out['micro'][v]=json.loads((W/('micro-'+v+'.json')).read_text())
ids=subprocess.check_output(['docker','ps','-q'],text=True).split()
for d in json.loads(subprocess.check_output(['docker','inspect',*ids],text=True)):
 if (d['Config'].get('Labels') or {}).get('cody.startup-mechanism-helper'):continue
 out['live'][d['Name'].lstrip('/')]={'id':d['Id'],'image':d['Image'],'started':d['State']['StartedAt'],'health':d['State'].get('Health',{}).get('Status'),'restarts':d['RestartCount'],'oom':d['State']['OOMKilled']}
out['remainingFixtures']=subprocess.check_output(['docker','ps','-aq','--filter','label=cody.startup-mechanism-fixture=true'],text=True).split();out['remainingNetworks']=subprocess.check_output(['docker','network','ls','-q','--filter','label=cody.startup-mechanism-fixture=true'],text=True).split();assert not out['remainingFixtures'] and not out['remainingNetworks']
for n in ['terry','marsha']:assert out['live'][n]['health']=='healthy' and out['live'][n]['restarts']==0 and not out['live'][n]['oom']
out['candidateManifest']=json.loads((W/'mem0-lean/package.json').read_text());out['candidateLockSha256']=hashlib.sha256((W/'mem0-lean/package-lock.json').read_bytes()).hexdigest();(W/'final-mechanism-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))

