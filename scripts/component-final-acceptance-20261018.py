"""Final post-host checks, preserving the earlier acceptance receipts."""
import json, shutil, subprocess, time
from pathlib import Path
base=Path('/opt/openclaw/backups/components-20261018')
names=['wilma','vivian','inga','maggie','gohzed','grogar','terry','edith','marsha','amanda','victor']
source=Path('/home/jackadmin/components-20261018/accept.py').read_text()
source=source.replace('agent:main:cody-components-acceptance','agent:main:cody-components-post-host')
source=source.replace('Read-only acceptance. State one existing fact from automatically supplied Hindsight memories.', 'Read-only post-restart memory acceptance. From automatically supplied Hindsight memories, state what changed during the October 18 component maintenance performed by Cody. If that maintenance fact is unavailable, say so.')
compile(source, 'post-host-accept.py', 'exec')
final_script=base/'post-host-accept.py';final_script.write_text(source)
results=[]
for name in names:
    work=base/name
    for filename in ['acceptance.json','capability.json','capability.stderr','memory-injection.log']:
        if (work/filename).exists():shutil.copy2(work/filename,work/('before-host-'+filename))
    with (work/'post-host-acceptance.log').open('w') as out:
        r=subprocess.run(['python3',str(final_script),name],stdout=out,stderr=subprocess.STDOUT,timeout=1050)
    assert r.returncode==0,name+' final acceptance failed; inspect protected log'
    versions={}
    for tool,args,expected in [('node',['--version'],'v24.22.0'),('gog',['--version'],'0.45.0'),('ntn',['--version'],'0.23.20'),('gh',['--version'],'2.102.0'),('himalaya',['--version'],'2.2.1'),('mcporter',['--version'],'0.15.0'),('summarize',['--version'],'0.25.2')]:
        p=subprocess.run(['docker','exec','-u','node',name,tool,*args],capture_output=True,text=True,timeout=45)
        assert p.returncode==0 and expected in p.stdout+p.stderr,name+' version failed: '+tool
        versions[tool]=(p.stdout+p.stderr).strip().splitlines()[0]
    d=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
    pid=d['State']['Pid'];rel=Path('/proc/'+str(pid)+'/cgroup').read_text().strip().split('::',1)[1]
    cg=Path('/sys/fs/cgroup')/rel.lstrip('/')
    stats=dict(line.split() for line in (cg/'memory.stat').read_text().splitlines())
    current=int((cg/'memory.current').read_text());events=dict(line.split() for line in (cg/'memory.events').read_text().splitlines())
    assert int(events['oom'])==0 and int(events['oom_kill'])==0
    a=json.loads((work/'acceptance.json').read_text())
    row={'agent':name,'accepted':True,'versions':versions,'memoryCurrentBytes':current,'memoryMinusInactiveFileBytes':current-int(stats.get('inactive_file',0)),'memoryEvents':events,'cronCount':a['cronCount'],'model':a['receipt'].get('effective'),'measuredAtUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    (work/'post-host-summary.json').write_text(json.dumps(row,indent=2));results.append(row)
    print(json.dumps(row),flush=True)
(base/'final-fleet-acceptance.json').write_text(json.dumps(results,indent=2))
