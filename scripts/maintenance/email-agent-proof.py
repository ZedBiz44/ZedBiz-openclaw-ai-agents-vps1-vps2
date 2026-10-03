import subprocess,pathlib,json,sys
n=sys.argv[1];assert n in ['terry','amanda','edith','gohzed','grogar','inga','maggie','marsha','victor','vivian','wilma']
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003')/n
prompt=b/'agent-proof-message.txt';prompt.write_text('Maintenance verification, read-only. Read your installed workspace skills/himalaya/SKILL.md using a shell tool. Run himalaya --version and himalaya account check. Verify both IMAP and SMTP show OK; do not print configuration, credentials or message contents. Use your external memory recall tool for a short VPS1 lookup. Report the email version, authentication status, and whether mail can be sent without explicit authorization. Do not send email, save drafts, change mailbox state, create memories or modify files.')
subprocess.run(['docker','cp',str(prompt),n+':/tmp/cody-email-proof.txt'],check=True)
with (b/'live-agent-proof.json').open('w') as f,(b/'live-agent-proof.stderr').open('w') as e:
 p=subprocess.run(['docker','exec',n,'openclaw','agent','--agent','main','--session-key','agent:main:cody-email-v2-20261003','--message-file','/tmp/cody-email-proof.txt','--timeout','180','--json'],stdout=f,stderr=e,timeout=240)
j=json.loads((b/'live-agent-proof.json').read_text());m=j['result']['meta'];r={'agent':n,'runId':j.get('runId'),'trace':m.get('executionTrace'),'tools':m.get('toolSummary'),'reply':m.get('finalAssistantVisibleText')};print(json.dumps(r,indent=2))
assert p.returncode==0 and r['trace']['winnerModel']==('gpt-6-astra' if n=='marsha' else 'gpt-6.1-sol') and r['trace']['fallbackUsed'] is False and r['tools']['failures']==0
expected='mem0_search' if n in ['terry','edith'] else 'agent_knowledge_recall' if n in ['gohzed','grogar','inga','maggie','marsha'] else 'memory_recall'
assert expected in r['tools']['tools'] and 'bash' in r['tools']['tools']
(b/'live-agent-proof-summary.json').write_text(json.dumps(r,indent=2))
