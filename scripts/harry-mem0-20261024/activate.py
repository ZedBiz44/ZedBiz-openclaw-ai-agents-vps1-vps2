import sys
sys.argv=['activate','maintenance']
exec(open('/root/cody-vps2-followup-20261023/followup.py').read().split('if action==')[0])
B=Path('/root/cody-harry-mem0-20261024')
proof=json.loads((B/'pilot-result.json').read_text());assert proof['passed'] and proof['cleaned']
p=Path('/root/.openclaw-harry/openclaw.json');before=p.read_bytes();c=json.loads(before)
assert c['plugins']['entries']['openclaw-mem0']['config']['oss']['llm']['config']['model']=='gpt-4.1-nano-2025-04-14'
assert not (B/'openclaw-before.json').exists()
(B/'openclaw-before.json').write_bytes(before)
idle('harry')
run(['systemctl','stop','openclaw-harry'])
try:
 c['plugins']['entries']['openclaw-mem0']['config']['oss']['llm']['config']['model']='gpt-6-luna'
 tmp=p.with_suffix('.luna.tmp');tmp.write_text(json.dumps(c,indent=2)+'\n');tmp.chmod(0o600);tmp.replace(p)
 check=json.loads(p.read_text());check['plugins']['entries']['openclaw-mem0']['config']['oss']['llm']['config']['model']='gpt-4.1-nano-2025-04-14';assert check==json.loads(before)
 (B/'activation.json').write_text(json.dumps({'oldModel':'gpt-4.1-nano-2025-04-14','newModel':'gpt-6-luna','beforeSha256':hashlib.sha256(before).hexdigest(),'afterSha256':sha(p),'onlyModelChanged':True,'time':int(time.time())},indent=2))
finally:run(['systemctl','start','openclaw-harry'])
emit({'changed':True,'serviceStarted':True})
