"""Readiness and actual runtime acceptance for one already activated agent."""
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

name = sys.argv[1]
assert name in {'wilma', 'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
work = Path('/opt/openclaw/backups/fleet-20261018')/name
start = time.monotonic()
while time.monotonic()-start < 420:
    d = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
    try:
        http = urllib.request.urlopen('https://'+name+'.zbiz.ca/healthz', timeout=5).status
    except Exception:
        http = None
    if http == 200 and d['State']['Health']['Status'] == 'healthy':
        break
    time.sleep(5)
else:
    raise RuntimeError('readiness deadline exceeded')
assert d['RestartCount'] == 0 and not d['State']['OOMKilled'], 'automatic restart or OOM requires review'
manifest = json.loads((Path('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json').read_text())
identities = {i['ref']: i['id'] for i in manifest['images']}
assert d['Image'] == identities[d['Config']['Image']]
for container in [name, name+'-asana-mcp']:
    i = json.loads(subprocess.check_output(['docker', 'inspect', container], text=True))[0]
    assert i['State']['Health']['Status'] == 'healthy'
assert subprocess.check_output(['systemctl', 'show', 'openclaw-'+name, '-p', 'Result', '--value'], text=True).strip() == 'success'

def rpc(method, params=None):
    args = ['docker', 'exec', '-u', 'node', name, 'node', '/app/openclaw.mjs', 'gateway', 'call', method, '--json']
    if params:
        args += ['--params', json.dumps(params)]
    p = subprocess.run(args, capture_output=True, text=True, timeout=90)
    assert p.returncode == 0, 'RPC failed; output withheld'
    value = json.loads(p.stdout[p.stdout.index('{'):])
    f = work/(method+'-after.json'); f.write_text(json.dumps(value)); f.chmod(0o600)
    return value

health = rpc('health')
assert health.get('ok') is True
old_health = json.loads((work/'health-before.json').read_text())
for channel, details in old_health.get('channels', {}).items():
    for account, state in details.get('accounts', {}).items():
        current = health.get('channels', {}).get(channel, {}).get('accounts', {}).get(account, {})
        for field in ['running', 'connected']:
            if state.get(field) is True:
                assert current.get(field) is True, 'channel regression: '+channel+'/'+account+'/'+field
version = subprocess.check_output(['docker', 'exec', '-u', 'node', name, 'node', '/app/openclaw.mjs', '--version'], text=True, timeout=30)
assert '2026.10.4' in version
before = json.loads((work/'cron.list-before.json').read_text())
after = rpc('cron.list', {'includeDisabled': True})
keys = ['id', 'name', 'enabled', 'schedule', 'sessionTarget', 'wakeMode', 'payload', 'delivery']
normalize = lambda obj: sorted([{k: job.get(k) for k in keys} for job in obj['jobs']], key=lambda job: job['id'])
assert normalize(before) == normalize(after), 'schedule definitions changed'
config = json.loads((Path('/opt/openclaw/agents')/name/'config/openclaw.json').read_text())
backend = config.get('plugins', {}).get('slots', {}).get('memory')
memory_tool = 'agent_knowledge_recall' if backend == 'hindsight-openclaw' else 'mem0_search' if backend == 'openclaw-mem0' else 'memory_recall'
prompt = ('Read-only upgrade acceptance. You MUST use '+memory_tool+' to recall one existing ZedBiz or VPS1 memory from your configured backend; local Markdown memory_search is not sufficient. Get your own Asana user identity and fetch Notion page 3a4a3e33d58180bb8d8ac911f0f4163e. Also use a harmless shell tool to check command availability for gog, himalaya, ffmpeg, ntn and gh. Return only the memory tool used and short recalled fact, Asana name/GID, Notion title and whether those binaries exist. Report any backend failure plainly. Do not send external messages, edit files, create tasks or memories, or delegate.')
p = subprocess.run(['docker', 'exec', '-u', 'node', name, 'node', '/app/openclaw.mjs', 'agent', '--agent', 'main', '--session-key', 'agent:main:cody-fleet-10-4-acceptance', '--message', prompt, '--timeout', '240', '--json'], capture_output=True, text=True, timeout=270)
for suffix, content in [('json', p.stdout), ('stderr', p.stderr)]:
    f = work/('capability.'+suffix); f.write_text(content); f.chmod(0o600)
assert p.returncode == 0, 'actual runtime test failed; inspect protected receipt'
obj = json.loads(p.stdout[p.stdout.index('{'):])
receipt = obj.get('result', {}).get('meta', {}).get('agentMeta', {}).get('terminalReceipt', {})
assert receipt and receipt.get('rerouted') is False, 'missing receipt or fallback'
tools = receipt.get('successfulToolNames', [])
assert any('asana_get_user' in t for t in tools), 'Asana identity tool not proved'
assert any('notion' in t and ('fetch' in t or 'retrieve' in t) for t in tools), 'Notion access not proved'
assert any(memory_tool in t for t in tools), 'configured memory backend tool not proved'
channels = {k: {a: {x: v.get(x) for x in ['configured', 'running', 'connected', 'lastError']} for a, v in channel.get('accounts', {}).items()} for k, channel in health.get('channels', {}).items()}
result = dict(agent=name, accepted=True, http=200, containerId=d['Id'], image=d['Image'], cronCount=len(after['jobs']), schedulesUnchanged=True, channels=channels, memoryBackend=backend, requiredMemoryTool=memory_tool, receipt=receipt)
(work/'acceptance.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result), flush=True)
print(json.dumps(obj.get('result', {}).get('payloads', [])), flush=True)

