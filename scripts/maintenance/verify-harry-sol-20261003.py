import pathlib,json,hashlib,subprocess,urllib.request
b=pathlib.Path('/root/cody-harry-maintenance-20261003')
live=pathlib.Path('/root/.openclaw-harry')
before=b/'activation-before-state'
c=json.loads((live/'openclaw.json').read_text())
old=json.loads((before/'openclaw.json').read_text())
s=(b/'activation-model.json').read_text();result=json.loads(s[s.index('{'):])
meta=result['result']['meta']
trace=meta['executionTrace']
assert trace['winnerModel']=='gpt-6.1-sol' and not trace['fallbackUsed']
assert meta['toolSummary']['calls']>=1 and meta['toolSummary']['failures']==0
assert (b/'proof-token.txt').read_text().strip() in meta['finalAssistantVisibleText']
assert c['agents']['defaults']['model']=={'primary':'openai/gpt-6.1-sol','fallbacks':[]}
assert c['auth']['order']['openai']==['openai:jzedbiz@gmail.com']
assert c['plugins']['entries']['codex']['config']['appServer']['command']=='/usr/bin/codex'
core={}
for p in (before/'workspace').glob('*.md'):
 current=live/'workspace'/p.name
 core[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256(current.read_bytes()).hexdigest()
assert all(core.values())
preserved={key:c.get(key)==old.get(key) for key in ['channels','cron','skills']}
assert all(preserved.values()),preserved
health={str(p):urllib.request.urlopen(f'http://127.0.0.1:{p}/health',timeout=10).status for p in [4100,4200,4300]}
evidence={'runId':result['runId'],'status':result['status'],'executionTrace':trace,'toolSummary':meta['toolSummary'],'proofMatched':True,'coreFilesPreserved':core,'settingsPreserved':preserved,'health':health,'codexVersion':subprocess.check_output(['/usr/bin/codex','--version'],text=True).strip(),'openclawVersion':json.loads(pathlib.Path('/opt/openclaw-harry/node_modules/openclaw/package.json').read_text())['version'],'authOrder':c['auth']['order']['openai'],'fallbacks':c['agents']['defaults']['model']['fallbacks']}
(b/'final-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
print(json.dumps(evidence,indent=2))
