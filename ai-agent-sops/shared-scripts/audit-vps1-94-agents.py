#!/usr/bin/env python3
"""Read-only comparison of upgraded VPS1 agents against retained originals."""
import json,subprocess,pathlib,sys
base=pathlib.Path('/home/jackadmin/openclaw-backups/fleet94-20260912')
for n in sys.argv[1:]:
 assert n in {'edith','vivian','maggie','inga','gohzed','grogar','wilma','victor','marsha','amanda'}
 info=json.loads(subprocess.check_output(['docker','inspect',n],text=True))[0]
 code="""const fs=require('fs'),crypto=require('crypto');
const a=JSON.parse(fs.readFileSync('/before/config/openclaw.json')),b=JSON.parse(fs.readFileSync('/after/config/openclaw.json'));
const equal=(x,y)=>JSON.stringify(x)===JSON.stringify(y);
const files=['AGENTS.md','TOOLS.md'].map(f=>{let x='/before/workspace/'+f,y='/after/workspace/'+f;if(!fs.existsSync(x)&&!fs.existsSync(y))return [f,'absent-both'];return [f,fs.existsSync(x)&&fs.existsSync(y)&&fs.readFileSync(x).equals(fs.readFileSync(y))?'unchanged':'CHANGED'];});
const slot=a.plugins?.slots?.memory;
console.log(JSON.stringify({files,modelsUnchanged:equal(a.agents?.defaults?.model,b.agents?.defaults?.model),memorySlotUnchanged:slot===b.plugins?.slots?.memory,memoryConfigUnchanged:equal(a.plugins?.entries?.[slot]?.config,b.plugins?.entries?.[slot]?.config),sessionVisibilityPreserved:(a.tools?.sessions?.visibility??'tree')===b.tools?.sessions?.visibility,swarm:b.tools?.swarm,agentToAgent:b.tools?.agentToAgent,maxSpawnDepth:b.agents?.defaults?.subagents?.maxSpawnDepth}));"""
 raw=subprocess.check_output(['docker','run','--rm','--user','root','--network','none','--entrypoint','node','-v',str(base/n/'original')+':/before:ro','-v','/opt/openclaw/agents/'+n+':/after:ro',info['Config']['Image'],'-e',code],text=True)
 data=json.loads(raw);data.update(name=n,image=info['Config']['Image'],health=info['State'].get('Health',{}).get('Status'),restarts=info['RestartCount'])
 raw=(base/n/'live-post-upgrade.json').read_text();post=json.JSONDecoder().raw_decode(raw[raw.index('{'):])[0];data['postUpgradeFindings']=post['findings']
 data['backupSha256']=(base/n/'backup.sha256').read_text().strip()
 (base/n/'final-audit.json').write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(data),flush=True)
