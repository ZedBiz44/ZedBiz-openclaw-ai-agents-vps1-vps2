#!/usr/bin/env python3
"""Victor's administrator SSH route. Credentials stay in secret injection."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap

def main():
    routes=json.loads((Path(__file__).parent/'fleet-admin-routes.json').read_text())
    if len(sys.argv)<2 or sys.argv[1] not in routes:
        print('Usage: victor-ssh.py vps1|vps2|vps3|vps4 [remote command]',file=sys.stderr)
        return 2
    route=routes[sys.argv[1]]
    match=re.search(r'-----BEGIN ([A-Z ]+PRIVATE KEY)-----\s*(.*?)\s*-----END \1-----',os.environ.get('VICTOR_SSH_KEY',''),re.S)
    if not match:
        raise RuntimeError('VICTOR_SSH_KEY missing or malformed')
    key='-----BEGIN '+match[1]+'-----\n'+'\n'.join(textwrap.wrap(re.sub(r'\s+','',match[2]),64))+'\n-----END '+match[1]+'-----\n'
    with tempfile.TemporaryDirectory(prefix='victor-admin-') as directory:
        p=Path(directory)/'key';p.write_text(key);p.chmod(0o600)
        known=Path(directory)/'known_hosts';known.write_text(route['host']+' '+route['hostKey']+'\n');known.chmod(0o600)
        cmd=['ssh','-i',str(p),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(known),route['user']+'@'+route['host']]
        cmd.extend(sys.argv[2:])
        return subprocess.run(cmd).returncode
if __name__=='__main__':
    raise SystemExit(main())
