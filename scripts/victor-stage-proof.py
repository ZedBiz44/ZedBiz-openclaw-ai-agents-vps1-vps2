"""Isolated model/tool check with an explicit primary and no fallback chain."""
import os,pathlib,subprocess
work=pathlib.Path('/home/jackadmin/victor-10.4-20261017')
env=os.environ.copy();env['REHEARSAL_NETWORK']='bridge'
prefix=['python3',str(work/'scripts/victor-rehearsal.py'),'zedbiz/openclaw-victor:2026.10.4-pilot-20261017']
node_env=dict(env,REHEARSAL_ENTRYPOINT='node')
subprocess.run(prefix+['/checks/stage-proof-config.cjs','prepare'],env=node_env,check=True)
args=prefix+['agent','--local','--agent','main','--session-key','agent:main:cody-10-4-stage-proof','--thinking','low','--json','--message','Run a harmless shell tool to read /etc/os-release. Then use memory_recall for a short read-only lookup of VPS1. Do not send messages, create memories, or change files. Report the OS and whether the memory lookup succeeded. Use actual tools.']
try:
    with (work/'stage-local-proof-credentials.json').open('w') as out,(work/'stage-local-proof-credentials.stderr').open('w') as err:
        result=subprocess.run(args,env=env,stdout=out,stderr=err)
finally:
    subprocess.run(prefix+['/checks/stage-proof-config.cjs','restore'],env=node_env,check=True)
print('Stage proof exit:',result.returncode)
raise SystemExit(result.returncode)
