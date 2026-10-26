"""Repair the known versioned boot gate; test the actual entrypoint before live retry."""
import pathlib,subprocess,json,hashlib,sys,os,time,re
P=pathlib.Path;os.umask(0o077);w=P('/opt/openclaw/backups/release-20261024-marsha');live=P('/opt/openclaw/agents/marsha');stage=w/'rehearsal';name='cody-marsha-10-6-full-start';action=sys.argv[1]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def patch(base):
 p=base/'workspace/post-start.sh';assert sha(p)=='4e7372f7242e983c965971e96cece88fed5ca5a1cba2e2a0d2c965f8c28d875f'
 s=p.read_text();old='node /opt/zedbiz/verify-workshop-model-10-4.cjs || exit $?';new='node /home/node/.openclaw/workspace/verify-startup-10-6.cjs || exit $?';assert s.count(old)==1;s=s.replace(old,new)
 oldIdentity='openclaw agents set-identity --agent main --name "$AGENT_NAME" '+chr(92)+'\n  --avatar avatars/openclaw.png >/dev/null 2>&1 || true'
 replacement='\n'.join(['if node /home/node/.openclaw/workspace/verify-startup-10-6.cjs --identity-is-current >/dev/null 2>&1; then','  echo "[post-start] Agent identity already configured"','else','  openclaw agents set-identity --agent main --name "$AGENT_NAME" '+chr(92),'    --avatar avatars/openclaw.png >/dev/null 2>&1 || exit $?','fi'])
 assert s.count(oldIdentity)==1,'Identity invocation differs; inspect instead of broad edits'
 s=s.replace(oldIdentity,replacement)
 guard=base/'workspace/verify-startup-10-6.cjs';guard.write_bytes((w/'verify-startup-10-6.cjs').read_bytes());os.chown(guard,1000,1000)
 stat=p.stat();p.write_text(s);os.chown(p,stat.st_uid,stat.st_gid);os.chmod(p,stat.st_mode&0o777)
 assert sha(base/'workspace/github-runtime-auth/restore-native.py')=='88e951b9bdf25d7dc7fb4d0dcf8c1af71ff3a2ca0d42013a94b3ee7b3e0ae759'
 return {'postStartSha256':sha(p),'guardSha256':sha(guard),'githubAuthHelperUnchanged':True}
def args():
 a=['docker','run','-d','--name',name,'--network','openclaw','--network','release-20261023-hindsight-rehearsal','--memory','3g','--memory-swap','3g','--env-file',str(w/'runtime.env'),'--user','node']
 for key in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR']:a+=['-e',key+'=1']
 for m in json.loads((w/'mounts.json').read_text()):
  src=m['Source'];dst=m['Destination']
  if src in ['/var/run/docker.sock','/dev/shm']:continue
  if src.startswith(str(live)+'/'):src=str(stage/src[len(str(live))+1:]);mode='' if m['RW'] else ':ro'
  else:mode=':ro'
  if src in ['/opt/openclaw/shared/bin/'+x for x in ['gog','mcporter','summarize']]:src='/opt/openclaw/shared/tools-20261023/bin/'+P(src).name+'-wrapper'
  a+=['-v',src+':'+dst+mode]
 return a+['-v',str(w/'wiki')+':/opt/openclaw/shared/knowledge/wiki',json.loads((w/'build.json').read_text())['candidate'],'sh','-c','bash /home/node/.openclaw/workspace/post-start.sh && exec openclaw gateway run --bind lan --port 3005']
if action=='test-full':
 result=patch(stage);(w/'startup-repair-clone.json').write_text(json.dumps(result))
 subprocess.run(['docker','start','cody-marsha-hindsight-1-0'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(args(),check=True,stdout=subprocess.DEVNULL);started=time.monotonic();log=''
 try:
  for _ in range(160):
   d=json.loads(subprocess.check_output(['docker','inspect',name]))[0];p=subprocess.run(['docker','logs',name],capture_output=True,text=True);log=p.stdout+p.stderr
   assert d['State']['Running'],'Full startup fixture exited; inspect log'
   if d['State'].get('Health',{}).get('Status')=='healthy' and 'startup phase: sidecars.subagent-recovery' in log:break
   time.sleep(3)
  else:raise RuntimeError('Full startup fixture readiness deadline')
  assert '[post-start] Agent identity already configured' in log
  result.update(passed=True,defaultEntrypointUsed=True,productionPostStartUsed=True,postStartCompleted=True,identityCliSkippedOnlyWhenAlreadyCorrect=True,restarts=d['RestartCount'],elapsedWallSeconds=round(time.monotonic()-started,1))
  (w/'full-start-proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
 finally:
  (w/'full-start.log').write_text(log);subprocess.run(['docker','stop',name],check=True,stdout=subprocess.DEVNULL);subprocess.run(['docker','rm',name],check=True,stdout=subprocess.DEVNULL)
elif action=='apply-live':
 assert json.loads((w/'full-start-proof.json').read_text())['passed']
 assert subprocess.run(['docker','inspect','marsha'],capture_output=True).returncode!=0,'Live service must be stopped'
 result=patch(live);(w/'startup-repair-live.json').write_text(json.dumps(result));print(json.dumps(result),flush=True)
else:raise SystemExit('Unsupported phase')

