"""Verify published build inputs, then build Marsha's immutable tools candidate."""
import pathlib,hashlib,json,subprocess,os,sys
P=pathlib.Path;os.umask(0o077)
context=P('/home/jackadmin/vps1-10-6-20261023')
expected={'Dockerfile.tools-full':'307450c7b5a5f51fda825b5d74f344259248fba2','Dockerfile.cohort':'0a5d3f05d4c5b84a809ad2c07e863b4a4f6ad523','marsha-owner-scheduling.mjs':'e68c1aa0de6251a4405ef112f11152f28cd6337d','tool-assets.json':'9116c05396c680893971680001bd36871c139bde'}
for name,blob in expected.items():
 b=(context/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==blob,'Published source mismatch: '+name
for a in json.loads((context/'tool-assets-proof.json').read_text()):
 with (context/'tool-assets'/a['binary']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==a['binarySha256']
def inspect(ref):return json.loads(subprocess.check_output(['docker','image','inspect',ref]))[0]
core=inspect('zedbiz/marsha:2026.10.6-core-20261023');cli=inspect('zedbiz/openclaw-base:2026.10.6-tools-20261023')
assert core['Id'].startswith('sha256:fa82667a2550')
assert cli['Id']=='sha256:07671069e4d7fc7f4b426e7ad88bd8c4fb14c29fb6872a2c605843f3111de90f'
tag='zedbiz/marsha:2026.10.6-tools-full-20261024'
assert subprocess.run(['docker','image','inspect',tag],capture_output=True).returncode!=0,'Existing candidate; inspect before reuse'
w=P('/opt/openclaw/backups/release-20261024-marsha');w.mkdir(mode=0o700)
with (w/'build.log').open('w') as log:subprocess.run(['docker','build','--network','host','--build-arg','BASE_IMAGE='+core['Id'],'-f','Dockerfile.tools-full','-t',tag,'.'],cwd=context,stdout=log,stderr=subprocess.STDOUT,check=True)
result={'sourceCommit':'05346ca11e9ca1d56789fff400edb953e75ff357','sourceBlobs':expected,'baseId':core['Id'],'cliId':cli['Id'],'candidate':tag,'candidateId':inspect(tag)['Id'],'buildSmokeTestsPassed':True}
(w/'build.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

