"""Safe pilot inspection and a non-delivered shell/memory response."""
import json,pathlib,subprocess,sys
work=pathlib.Path('/home/jackadmin/amanda-10.4-20261017')
mode=sys.argv[1]
if mode=='inspect':
    d=json.loads(subprocess.check_output(['docker','inspect','amanda']))[0]
    c=json.loads(subprocess.check_output(['docker','exec','amanda','cat','/home/node/.openclaw/openclaw.json']))
    print(json.dumps({'image':d['Image'],'status':d['State']['Status'],'health':d['State'].get('Health',{}).get('Status'),'restartCount':d['RestartCount'],'memoryBytes':d['HostConfig']['Memory'],'memorySwapBytes':d['HostConfig']['MemorySwap'],'ports':d['HostConfig']['PortBindings'],'primary':c['agents']['defaults']['model']['primary'],'openaiAuthOrder':c['auth']['order']['openai']},indent=2))
    for args in [['openclaw','--version'],['codex','--version'],['curl','-fsS','--max-time','10','http://127.0.0.1:3000/healthz']]:
        subprocess.run(['docker','exec','amanda']+args,check=True)
elif mode=='proof':
    prompt='Run a harmless shell tool to read /etc/os-release. Then use memory_recall for a short read-only lookup of VPS1. Also call the Asana MCP asana_get_user tool with user_gid me to verify your own Amanda account. Do not send messages, create memories, or change files or Asana records. Report the OS, whether memory lookup succeeded, and your Asana identity. Use actual tools.'
    with (work/'live-proof.json').open('w') as out,(work/'live-proof.stderr').open('w') as err:
        p=subprocess.run(['docker','exec','amanda','openclaw','agent','--agent','main','--session-key','agent:main:cody-10-4-live-proof','--thinking','low','--message',prompt,'--json'],stdout=out,stderr=err)
    subprocess.run(['python3',str(work/'scripts/summarize-proof.py'),str(work/'live-proof.json')],check=True)
    j=json.loads((work/'live-proof.json').read_text());m=j.get('result',j).get('meta',{})
    assert p.returncode==0 and m['executionTrace']['winnerModel']=='gpt-6.1-sol' and m['executionTrace']['fallbackUsed'] is False
    assert m['toolSummary']['failures']==0 and {'bash','memory_recall'}<=set(m['toolSummary']['tools'])
    assert any('asana_get_user' in t for t in m['toolSummary']['tools']), 'Missing integrated Asana proof'
else:raise SystemExit('Expected inspect or proof')

