"""Resume the verified prepared upgrade; the original Gateway never resumed after the missing-directory failure."""
import pathlib,json,subprocess,os,signal,hashlib,sqlite3
P=pathlib.Path;os.umask(0o077);agent='vivian';live=P('/opt/openclaw/agents/vivian');A=P('/opt/openclaw/backups/fleet-10-6-20261024/vivian');prepared=A/'failed-preactivation-state';restored=A/'restored-original-unused';M=P('/opt/openclaw/backups/mem0-repair-20261024-r2');R=P('/opt/openclaw/recovery/release-20261024-fleet-tools')
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,label,timeout=120):
 print(json.dumps({'vivianRepairPhase':label}),flush=True)
 with (A/(label+'.private.log')).open('w') as out:r=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
 assert r.returncode==0,label+' failed'
pause=json.loads((A/'operator-repair-pause.json').read_text());assert pause['originalGatewayNeverResumed'] and not (A/'resume-original.private.log').exists()
assert subprocess.run(['docker','inspect','vivian'],capture_output=True).returncode!=0
for pid in pause['rollbackWorkerPids']:
 data=P('/proc/'+str(pid)+'/stat').read_text().split(') ',1)[1].split();assert data[0]=='Z' and int(data[49])==0,'Rollback extraction still active or failed'
for key in ['activationPid','coordinatorPid']:
 pid=pause[key];assert P('/proc/'+str(pid)+'/comm').read_text().strip()=='python3';assert P('/proc/'+str(pid)+'/stat').read_text().split(') ',1)[1].split()[0] in ['T','t']
lint=json.loads((A/'lint.json').read_text());assert lint.get('checksRun')==105 and not any(f['severity'] in ['critical','error'] for f in lint['findings'])
cfg=json.loads((A/'config-before.json').read_text());c=json.loads((prepared/'config/openclaw.json').read_text())
for key in ['channels','mcp','tools']:assert c.get(key)==cfg.get(key)
for key in ['model','models','modelPolicy','thinkingDefault','timeoutSeconds']:assert c['agents']['defaults'].get(key)==cfg['agents']['defaults'].get(key)
assert c['gateway']['auth']==cfg['gateway']['auth'] and c['plugins']['slots']==cfg['plugins']['slots'] and c['plugins']['entries']['memory-lancedb']['config']==cfg['plugins']['entries']['memory-lancedb']['config']
protected=json.loads((A/'protected-files.json').read_text());assert all(sha(prepared/p)==v for p,v in protected['skills'].items())
instructions=protected['instructions']
for n,text in instructions.items():
 f=prepared/'workspace'/n
 if f.exists() and f.read_text()==text:continue
 if n=='TOOLS.md' and not f.exists():assert text.strip() in (prepared/'workspace/AGENTS.md').read_text()
 elif n=='AGENTS.md':assert f.read_text().strip()==(text.rstrip()+'\n\n## Tools\n\n### Local notes (migrated from TOOLS.md)\n\n'+instructions.get('TOOLS.md','').strip()).strip()
 else:raise AssertionError('Protected instruction differs: '+n)
old=json.loads((A/'cron-before.json').read_text());db=sqlite3.connect('file:'+str(prepared/'config/state/openclaw.sqlite')+'?mode=ro',uri=True)
cols=[r[1] for r in db.execute('pragma table_info(cron_jobs)')];rows=db.execute('select * from cron_jobs').fetchall();db.close();assert cols==old['columns'];idx=cols.index('declaration_key');retired=[r for r in old['rows'] if str(r[idx]).startswith('skill-collection-review:')];kept=[tuple(r) for r in old['rows'] if r not in retired];assert sorted(rows)==sorted(kept)
assert json.loads((A/'external-memory-restore.json').read_text())['passed']
catalog=json.loads((R/'catalog.json').read_text());assert json.loads((R/'archive-proof.json').read_text())['allImageIdsVerified'];target='zedbiz/openclaw-base:2026.10.6-tools-full-20261023';sideTarget='zedbiz/asana-http-mcp:2.0.0-components-20261023';ids={v['ref']:v['id'] for v in catalog['images']}
for ref in [target,sideTarget]:assert json.loads(subprocess.check_output(['docker','image','inspect',ref]))[0]['Id']==ids[ref]
assert live.resolve()==live and prepared.resolve()==prepared and not restored.exists();assert json.loads((live/'config/openclaw.json').read_text())==cfg
for key in ['activationPid','coordinatorPid']:os.kill(pause[key],signal.SIGKILL)
live.rename(restored);prepared.rename(live)
scripts=live/'config/scripts';assert not scripts.is_symlink();scripts.mkdir(mode=0o755,exist_ok=True);os.chown(scripts,1000,1000);guard=scripts/'verify-runtime-10-6.cjs';guard.write_bytes((M/'verify-vps1-runtime-10-6.cjs').read_bytes());os.chown(guard,1000,1000)
post=live/'workspace/post-start.sh';text=post.read_text();assert 'verify-runtime-10-6.cjs' not in text;line='node /home/node/.openclaw/scripts/verify-runtime-10-6.cjs vivian || exit $?\n'
if text.startswith('#!'):first,rest=text.split('\n',1);text=first+'\n'+line+rest
else:text=line+text
post.write_text(text);os.chown(post,1000,1000)
compose=(A/'compose-before.yml').read_text();manifest=P('/opt/openclaw/recovery/fleet-20261018/vivian/manifest.json');m=json.loads((A/'manifest-before.json').read_text());assert sha(m['wrapper'])==m['wrapper_sha256']
for v in m['images']:
 replacement=sideTarget if 'asana-http-mcp:' in v['ref'] else target;assert compose.count(v['ref'])==1;compose=compose.replace(v['ref'],replacement)
for binary in ['gog','mcporter','summarize']:
 oldPath='/opt/openclaw/shared/bin/'+binary
 if oldPath+':' in compose:assert compose.count(oldPath+':')==1;compose=compose.replace(oldPath+':','/opt/openclaw/shared/tools-20261023/bin/'+binary+'-wrapper:')
(live/'docker-compose.yml').write_text(compose);m.update(archive=catalog['archive'],sha256=catalog['sha256'],images=[v for v in catalog['images'] if v['ref'] in [target,sideTarget]]);manifest.write_text(json.dumps(m,indent=2))
(A/'preservation.json').write_text(json.dumps({'passed':True,'skills':len(protected['skills']),'userSchedulesPreserved':len(kept),'retiredBuiltinReviews':len(retired),'memorySlot':'memory-lancedb','target':target,'targetId':ids[target],'sidecar':sideTarget,'sidecarId':ids[sideTarget],'resumedPreparedStateWithoutOriginalGatewayAdmission':True}))
run(['systemctl','start','openclaw-vivian.service'],'repaired-managed-start',1500)
(A/'activation.json').write_text(json.dumps({'activated':True,'target':target,'targetId':ids[target],'sidecar':sideTarget,'sidecarId':ids[sideTarget],'awaitingLiveAcceptance':True,'checkpoint':str(A/'state-before.tar.gz'),'directoryAssumptionFixed':True}));print(json.dumps({'vivianActivated':True,'awaitingAcceptance':True}),flush=True)

