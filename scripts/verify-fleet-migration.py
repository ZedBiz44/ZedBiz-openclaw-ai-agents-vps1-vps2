"""Compare isolated migration against its preserved 9.8 state, without secrets."""
import json
from pathlib import Path
import sqlite3
import sys

name = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else 'rehearsal'
assert mode in {'rehearsal', 'live'}
assert name in {'wilma', 'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
live = Path('/opt/openclaw/agents')/name
stage = Path('/opt/openclaw/backups/fleet-20261018')/name/'rehearsal'

def rows(root):
    with sqlite3.connect('file:'+str(root/'config/state/openclaw.sqlite')+'?mode=ro', uri=True) as db:
        db.create_function('octet_length', 1, lambda x: len(x.encode() if isinstance(x, str) else x), deterministic=True)
        assert db.execute('PRAGMA quick_check').fetchall() == [('ok',)]
        return sorted(db.execute('SELECT * FROM cron_jobs').fetchall())

original, migrated = (live, stage) if mode == 'rehearsal' else (stage, live)
for db_path in (migrated/'agents').glob('*/agent/openclaw-agent.sqlite'):
    with sqlite3.connect('file:'+str(db_path)+'?mode=ro', uri=True) as db:
        db.create_function('octet_length', 1, lambda x: len(x.encode() if isinstance(x, str) else x), deterministic=True)
        assert db.execute('PRAGMA quick_check').fetchall() == [('ok',)], 'agent database integrity failed'
before = json.loads((original/'config/openclaw.json').read_text())
after = json.loads((migrated/'config/openclaw.json').read_text())
assert rows(original) == rows(migrated), 'schedule rows changed'
for field in ['model', 'models', 'modelPolicy', 'thinkingDefault', 'timeoutSeconds']:
    assert before['agents']['defaults'].get(field) == after['agents']['defaults'].get(field), 'model/timeout policy changed: '+field
assert before.get('plugins', {}).get('slots') == after.get('plugins', {}).get('slots'), 'memory backend changed'
assert before.get('mcp') == after.get('mcp'), 'MCP configuration changed unexpectedly'
for key in ['AGENTS.md', 'SOUL.md', 'USER.md', 'IDENTITY.md']:
    assert (migrated/'workspace'/key).exists(), 'core file missing: '+key
merged = len((migrated/'workspace/AGENTS.md').read_text())
budget = after['agents']['defaults'].get('bootstrapMaxChars', 20000)
print(json.dumps(dict(agent=name, cronRowsEqual=True, cronCount=len(rows(stage)), modelPolicyPreserved=True,
                      memoryBackendPreserved=True, mcpPreserved=True, agentsCharacters=merged,
                      bootstrapBudget=budget, needsBudgetIncrease=merged>budget)), flush=True)

