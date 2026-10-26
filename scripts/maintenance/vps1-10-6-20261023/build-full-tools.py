"""Build a selected core cohort's tool revision without altering running agents."""
import hashlib,json,pathlib,subprocess,sys
cohort=sys.argv[1];assert cohort in ['openclaw-base','amanda','victor','wilma','grogar','maggie','marsha']
root=pathlib.Path('/opt/openclaw/backups/release-20261023');out=root/'tool-builds';out.mkdir(exist_ok=True)
context=pathlib.Path('/home/jackadmin/vps1-10-6-20261023')
for item in json.loads((context/'tool-assets-proof.json').read_text()):
 with (context/'tool-assets'/item['binary']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==item['binarySha256']
base=f'zedbiz/{cohort}:2026.10.6-core-20261023';tag=f'zedbiz/{cohort}:2026.10.6-tools-full-20261023'
cli='zedbiz/openclaw-base:2026.10.6-tools-20261023'
image=lambda ref:subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',ref],text=True).strip()
assert image(cli)=='sha256:07671069e4d7fc7f4b426e7ad88bd8c4fb14c29fb6872a2c605843f3111de90f'
baseId=image(base)
with (out/(cohort+'.log')).open('w') as log:
 subprocess.run(['docker','build','--network','host','--build-arg','BASE_IMAGE='+base,'-f','Dockerfile.tools-full','-t',tag,'.'],cwd=context,stdout=log,stderr=subprocess.STDOUT,check=True)
result={'cohort':cohort,'coreId':baseId,'cliId':image(cli),'ref':tag,'id':image(tag),'buildSmokeTestsPassed':True}
(out/(cohort+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
