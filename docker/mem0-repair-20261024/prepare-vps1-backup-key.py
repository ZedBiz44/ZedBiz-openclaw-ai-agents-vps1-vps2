"""Create/read back the authorized VPS1 age recovery key in z-backups; never print secrets."""
import pathlib,subprocess,json,os,sys
P=pathlib.Path;os.umask(0o077);token=sys.stdin.read().strip();assert token.startswith('ops_');env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=token
W=P('/opt/openclaw/backups/private-recovery-20261024');W.mkdir(mode=0o700,exist_ok=True);key=W/'age-identity.txt';title='VPS1 agents backup unlocking code'
def op(args,input=None):
 p=subprocess.run(['op',*args],input=input,env=env,capture_output=True,text=True,timeout=90);assert p.returncode==0,'Private backup vault operation failed';return p.stdout
items=[x for x in json.loads(op(['item','list','--vault','z-backups','--format','json'])) if x['title']==title];assert len(items)<=1
if items:
 itemId=items[0]['id'];secret=op(['read','op://z-backups/'+itemId+'/password']).strip();assert secret.startswith('AGE-SECRET-KEY1'),'Existing key requires review'
 if key.exists():assert secret in key.read_text()
 else:key.write_text(secret+'\n');os.chmod(key,0o600)
else:
 if not key.exists():
  r=subprocess.run(['age-keygen','-o',str(key)],capture_output=True,text=True);assert r.returncode==0;os.chmod(key,0o600)
 secret=next(s for s in key.read_text().splitlines() if s.startswith('AGE-SECRET-KEY1'))
 template=json.loads(op(['item','template','get','Password','--format','json']));password=next(f for f in template['fields'] if f['id']=='password');password['value']=secret
 created=json.loads(op(['item','create','-','--vault','z-backups','--title',title,'--format','json'],json.dumps(template)));itemId=created['id']
assert op(['read','op://z-backups/'+itemId+'/password']).strip()==secret,'Vault key readback mismatch'
p=subprocess.run(['age-keygen','-y',str(key)],capture_output=True,text=True);assert p.returncode==0;recipient=p.stdout.strip();assert recipient.startswith('age1')
proof={'vault':'z-backups','itemId':itemId,'title':title,'type':'age-X25519','publicRecipient':recipient,'keyReadbackVerified':True,'localKeyPermissions':oct(key.stat().st_mode&0o777)}
(W/'key-receipt.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))

