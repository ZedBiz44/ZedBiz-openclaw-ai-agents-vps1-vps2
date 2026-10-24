"""Read-only cgroup and proportional process memory evidence; never print argv/env."""
import datetime
import json
from pathlib import Path
import subprocess

results = []
for name in ['amanda', 'victor', 'wilma', 'vivian', 'inga', 'maggie', 'gohzed', 'grogar', 'edith', 'terry', 'marsha']:
    p = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True)
    if p.returncode:
        results.append(dict(agent=name, running=False))
        continue
    obj = json.loads(p.stdout)[0]
    pid = obj['State']['Pid']
    if not pid:
        results.append(dict(agent=name, running=False))
        continue
    relative = next(line.split('::', 1)[1] for line in Path(f'/proc/{pid}/cgroup').read_text().splitlines() if line.startswith('0::'))
    cg = Path('/sys/fs/cgroup')/relative.lstrip('/')
    stats = dict(line.split() for line in (cg/'memory.stat').read_text().splitlines())
    current = int((cg/'memory.current').read_text())
    processes = []
    for child in (cg/'cgroup.procs').read_text().split():
        try:
            fields = {}
            for line in Path(f'/proc/{child}/smaps_rollup').read_text().splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    if key in {'Rss', 'Pss', 'Private_Dirty', 'Private_Clean'}:
                        fields[key] = int(value.split()[0])*1024
            processes.append(dict(pid=int(child), comm=Path(f'/proc/{child}/comm').read_text().strip(), **fields))
        except (FileNotFoundError, ProcessLookupError):
            pass
    results.append(dict(agent=name, running=True, containerId=obj['Id'], image=obj['Image'],
        health=obj['State'].get('Health', {}).get('Status'), restarts=obj['RestartCount'],
        oom=obj['State']['OOMKilled'], started=obj['State']['StartedAt'],
        memoryCurrent=current, dockerComparable=current-int(stats.get('inactive_file', 0)),
        anonymous=int(stats.get('anon', 0)), fileCache=int(stats.get('file', 0)),
        totalProcessPss=sum(p.get('Pss', 0) for p in processes), processes=processes))
print(json.dumps(dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(), agents=results)))

