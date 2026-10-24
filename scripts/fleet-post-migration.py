"""Apply the approved narrow per-agent adjustments after Doctor migration."""
import json
import math
from pathlib import Path
import sys

name, mode = sys.argv[1:]
assert name in {'wilma', 'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
assert mode in {'rehearsal', 'live'}
root = Path('/opt/openclaw/backups/fleet-20261018')/name/'rehearsal' if mode == 'rehearsal' else Path('/opt/openclaw/agents')/name
file = root/'config/openclaw.json'
cfg = json.loads(file.read_text())
defaults = cfg['agents']['defaults']
length = len((root/'workspace/AGENTS.md').read_text())
budget = defaults.get('bootstrapMaxChars', 20000)
if length > budget:
    defaults['bootstrapMaxChars'] = math.ceil((length+1000)/1000)*1000
mcp = cfg.setdefault('mcp', {})
old_ttl = mcp.get('sessionIdleTtlMs')
if old_ttl is None:
    mcp['sessionIdleTtlMs'] = 600000
file.write_text(json.dumps(cfg, indent=2)+'\n')
if name in {'marsha', 'grogar'}:
    post = root/'workspace/post-start.sh'
    old = 'python3 /home/node/.openclaw/workspace/workshop-runtime-repair-20260927/apply.py || exit $?'
    source = post.read_text()
    assert source.count(old) == 1, 'unexpected Workshop startup helper'
    post.write_text(source.replace(old, 'node /opt/zedbiz/verify-workshop-model-10-4.cjs || exit $?'))
print(json.dumps(dict(agent=name, mode=mode, agentsCharacters=length, bootstrapBefore=budget,
                      bootstrapAfter=defaults.get('bootstrapMaxChars', 20000), idleBefore=old_ttl,
                      idleAfter=mcp.get('sessionIdleTtlMs'), workshopImageVerification=name in {'marsha', 'grogar'})), flush=True)

