"""Export only explicitly selected secret-free rollout receipts for GitHub."""
import json,os,pathlib,tarfile
P=pathlib.Path;ROOT=P('/opt/openclaw/recovery/wiki-filelock-20261026')
assert json.loads((ROOT/'final-audit.json').read_text())['passed']
assert json.loads((ROOT/'index-proof.json').read_text())['passed']
names=['archive.json','catalog.json','cold-restore-proof.json','pilot-live-lint-proof.json','live-lint-proof.json','final-audit.json','offsite-proof.json','index-proof.json']
names += [row['agent']+'-acceptance.json' for row in json.loads((ROOT/'inventory.json').read_text())]
out=P('/tmp/cody-wiki-filelock-20261026/receipts.tar')
with tarfile.open(out,'w') as tar:
 for name in names:
  assert P(name).name==name and (ROOT/name).is_file()
  tar.add(ROOT/name,arcname=name,recursive=False)
os.chmod(out,0o644);print(json.dumps({'receiptCount':len(names),'privateLogsAndCredentialsExcluded':True}))
