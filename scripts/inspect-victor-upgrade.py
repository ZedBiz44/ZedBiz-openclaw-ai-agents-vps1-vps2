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
# Run verify-restored-databases.cjs with the target Node SQLite implementation.
# The host Python SQLite predates octet_length used in the agent schema.
