import os,sys,subprocess
from pathlib import Path
B=Path('/root/cody-harry-mem0-20261024');B.mkdir(mode=0o700,exist_ok=True);os.umask(0o077)
s=Path('/root/.openclaw-harry');e=os.environ.copy();e.update(HOME=str(s),OPENCLAW_STATE_DIR=str(s),OPENCLAW_CONFIG_PATH=str(s/'openclaw.json'),OP_SERVICE_ACCOUNT_TOKEN=(s/'.op.token').read_text().strip(),MEM0_TELEMETRY='false')
with (B/(sys.argv[1]+'.log')).open('w') as f:
 r=subprocess.run(['op','run','--no-masking','--env-file='+str(s/'.env'),'--','node',str(B/(sys.argv[1]+'.mjs'))],env=e,stdout=f,stderr=subprocess.STDOUT,timeout=240)
print('Test exit:',r.returncode)
sys.exit(r.returncode)
