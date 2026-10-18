"""Print selected non-secret inventory from the offline Victor rehearsal."""
import json, pathlib, sqlite3, subprocess
root = pathlib.Path('/restore')
cfg = json.loads((root/'config/openclaw.json').read_text())
print(json.dumps({
    'primary': cfg.get('agents', {}).get('defaults', {}).get('model'),
    'agentIds': [a.get('id') for a in cfg.get('agents', {}).get('list', [])],
    'pluginIds': list(cfg.get('plugins', {}).get('entries', {})),
    'installs': {k: {f: v.get(f) for f in ['source', 'spec', 'version', 'installPath']} for k, v in cfg.get('plugins', {}).get('installs', {}).items()},
    'channels': list(cfg.get('channels', {})),
}, indent=2))
for rel in ['config/state/openclaw.sqlite', 'agents/main/agent/openclaw-agent.sqlite']:
    path = root/rel
    with sqlite3.connect(str(path)) as conn:
        print(rel, 'quick_check', conn.execute('PRAGMA quick_check').fetchall())
        print('user_version', conn.execute('PRAGMA user_version').fetchone())
print('RESTORED_DATABASE_CHECKS_DONE')
