#!/usr/bin/env python3
"""Use Victor's injected key without printing or retaining its private value."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('agent',choices=['frank','suzy','harry','ruby','rocky'])
    parser.add_argument('--checks',action='store_true',help='Fresh gateway and required-channel checks on Frank, Harry or Suzy')
    args=parser.parse_args()
    if args.checks and args.agent not in ('frank','harry','suzy'):parser.error('Fresh checks are restricted to Frank, Harry and Suzy')
    folder=Path(__file__).resolve().parent
    routes=json.loads((folder/'fleet-diagnostic-routes.json').read_text())
    route=routes[args.agent]
    value=os.environ.get('VICTOR_SSH_KEY','')
    match=re.search(r'-----BEGIN ([A-Z ]+PRIVATE KEY)-----\s*(.*?)\s*-----END \1-----',value,re.S)
    if not match:raise ValueError('Injected VICTOR_SSH_KEY is missing or malformed')
    body=re.sub(r'\s+','',match[2])
    key='-----BEGIN '+match[1]+'-----\n'+'\n'.join(textwrap.wrap(body,64))+'\n-----END '+match[1]+'-----\n'
    with tempfile.TemporaryDirectory(prefix='victor-diagnostic-') as d:
        p=Path(d)/'key';p.write_text(key);p.chmod(0o600)
        known=Path(d)/'known_hosts';known.write_text(route['host']+' '+route['hostKey']+'\n');known.chmod(0o600)
        return subprocess.run(['ssh','-i',str(p),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(known),'root@'+route['host'],"SSH_ORIGINAL_COMMAND='"+('check ' if args.checks else 'inspect ')+args.agent+"' /usr/local/sbin/zedbiz-fleet-diagnostics"]).returncode

if __name__=='__main__':raise SystemExit(main())
