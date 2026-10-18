"""Sequential one-agent release executor; stop on any failed gate.

Choose rehearsal only for a new, not-yet-accepted capability cohort. Each
invocation handles one named agent and never advances to another agent.
"""
import json
from pathlib import Path
import subprocess
import sys

name, cohort = sys.argv[1:]
assert name in {'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
assert cohort in {'rehearse', 'proven'}
scripts = Path('/home/jackadmin/fleet-10.4-20261018/scripts')
work = Path('/opt/openclaw/backups/fleet-20261018')/name
image = 'zedbiz/'+name+':2026.10.4-workshop-20261018' if name in {'marsha', 'grogar'} else 'zedbiz/openclaw-base:2026.10.4-fleet-20261018'

def run(script, *args):
    print(json.dumps(dict(agent=name, step=script, args=args)), flush=True)
    subprocess.run(['python3', str(scripts/script), *args], check=True)

run('fleet-10-4-backup.py', name)
if cohort == 'rehearse':
    run('fleet-10-4-cli.py', name, 'rehearsal', image, 'doctor', '--fix', '--non-interactive')
    run('verify-fleet-migration.py', name, 'rehearsal')
    run('fleet-plugin-gate.py', name, 'rehearsal', image)
run('fleet-10-4-cli.py', name, 'live', image, 'doctor', '--fix', '--non-interactive')
run('verify-fleet-migration.py', name, 'live')
run('fleet-plugin-gate.py', name, 'live', image)
run('fleet-post-migration.py', name, 'live')
run('fleet-10-4-activate.py', name)
run('fleet-live-acceptance.py', name)
print(json.dumps(dict(agent=name, pipelineCompleted=True)), flush=True)

