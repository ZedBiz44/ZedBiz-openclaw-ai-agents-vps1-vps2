"""Read only, bounded runtime inventory; never print environments or process arguments."""
import datetime,json,subprocess
rows=[]
for name in ['amanda','amanda-asana-mcp']:
 d=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 raw=subprocess.check_output(['docker','exec',name,'node','-e',"const fs=require('fs');const r=n=>fs.readFileSync('/sys/fs/cgroup/'+n,'utf8').trim();console.log(JSON.stringify({current:r('memory.current'),swap:r('memory.swap.current'),events:r('memory.events'),stat:r('memory.stat')}))"],text=True)
 m=json.loads(raw);stat=dict(line.split() for line in m['stat'].splitlines());events=dict(line.split() for line in m['events'].splitlines())
 rows.append({'container':name,'image':d['Image'],'status':d['State']['Status'],'health':d['State'].get('Health',{}).get('Status'),'restarts':d['RestartCount'],'oomKilled':d['State']['OOMKilled'],'limitBytes':d['HostConfig']['Memory'],'memoryPlusSwapLimitBytes':d['HostConfig']['MemorySwap'],'currentBytes':int(m['current']),'inactiveFileBytes':int(stat.get('inactive_file',0)),'workingSetBytes':int(m['current'])-int(stat.get('inactive_file',0)),'swapBytes':int(m['swap']),'memoryEvents':events})
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'containers':rows},indent=2))
print(subprocess.check_output(['docker','top','amanda','-eo','pid,ppid,rss,comm'],text=True))
