import sys
sys.argv=['final-audit','audit']
exec(open('/root/cody-vps2-followup-20261023/followup.py').read().split("if action==")[0])
report={'bootId':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'agents':{}}
for n,port in [('frank',4300),('harry',4100),('suzy',4200)]:
 c=json.loads(Path('/root/.openclaw-'+n+'/openclaw.json').read_text())
 assert json.loads(Path('/opt/openclaw-'+n+'/node_modules/openclaw/package.json').read_text())['version']=='2026.10.6'
 health=obj(oc(n,['gateway','call','health','--json'],'final-health'));assert health['ok']
 for channel,details in health.get('channels',{}).items():
  if channel=='discord':assert all(v.get('connected') is True for v in details.get('accounts',{}).values())
 cron=obj(oc(n,['gateway','call','cron.list','--params','{"includeDisabled":true}','--json'],'final-cron'))
 old=json.loads(Path('/root/cody-vps2-20261023/'+n+'/cron.list-after.json').read_text())
 keys=['id','name','enabled','schedule','sessionTarget','wakeMode','payload','delivery']
 norm=lambda d:sorted([{k:j.get(k) for k in keys} for j in d['jobs']],key=lambda j:j['id'])
 assert norm(old)==norm(cron),'Schedule drift'
 plugins=obj(oc(n,['plugins','list','--json'],'final-plugins'))
 memory='openclaw-mem0' if n=='harry' else 'hindsight-openclaw';p=next(p for p in plugins['plugins'] if p['id']==memory)
 assert p['status']=='loaded' and p['version']==('1.2.1' if n=='harry' else '1.2.0')
 if n!='harry':
  cfg=c['plugins']['entries'][memory]['config'];assert cfg['memoryMode']=='context' and cfg['allowKnowledgeDelete'] is False and cfg['autoRecall'] and cfg['autoRetain']
 assert urllib.request.urlopen('https://'+n+'.zbiz.ca/healthz',timeout=15).status==200
 verify_asana(n,c['mcp']['servers']['asana']['url'],Path('/opt/zedbiz-asana-http-mcp'))
 stats=dict(l.split('=',1) for l in subprocess.check_output(['systemctl','show','openclaw-'+n,'-p','ActiveState','-p','Result','-p','NRestarts'],text=True).splitlines())
 assert stats['ActiveState']=='active' and stats['Result']=='success' and stats['NRestarts']=='0'
 events=dict(l.split() for l in Path('/sys/fs/cgroup/system.slice/openclaw-'+n+'.service/memory.events').read_text().splitlines());assert events['oom']=='0' and events['oom_kill']=='0'
 report['agents'][n]={'core':'2026.10.6','memoryVersion':p['version'],'publicHttp':200,'schedules':len(cron['jobs']),'service':stats,'memoryEvents':events}
report['failedUnits']=subprocess.check_output(['systemctl','--failed','--no-legend'],text=True);assert not report['failedUnits'].strip()
report['restartReview']=subprocess.check_output(['needrestart','-b','-r','l'],text=True)
report['disk']=subprocess.check_output(['df','-h','/'],text=True)
report['apt']=subprocess.check_output(['apt-get','-s','upgrade'],text=True)
report['versions']={x:subprocess.check_output([x,'--version'],text=True,stderr=subprocess.STDOUT,timeout=45).strip() for x in ['node','gog','gh','ntn','summarize','mcporter','codex','gemini']}
audit=subprocess.run(['npm','audit','--prefix','/opt/zedbiz-asana-http-mcp','--omit=dev','--json'],capture_output=True,text=True);assert audit.returncode==0;report['asanaAudit']=json.loads(audit.stdout)['metadata']['vulnerabilities']
(B/'final-audit.json').write_text(json.dumps(report,indent=2));emit(report)
