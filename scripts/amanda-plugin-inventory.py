import json,pathlib,subprocess
work=pathlib.Path('/home/jackadmin/amanda-10.4-20261017')
p=subprocess.run(['docker','exec','amanda','openclaw','plugins','list','--json'],capture_output=True,text=True)
(work/'live-plugins.json').write_text(p.stdout)
(work/'live-plugins.stderr').write_text(p.stderr)
j=json.loads(p.stdout)
rows=j.get('plugins',[]) if isinstance(j,dict) else j
ids={'discord','gradium','memory-lancedb','parallel','perplexity','tavily','codex','openai','deepseek','moonshot','qwen'}
print(json.dumps([{k:v.get(k) for k in ['id','version','status','origin','enabled']} for v in rows if v.get('id') in ids],indent=2))
raise SystemExit(p.returncode)
