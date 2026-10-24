import subprocess,json,pathlib,sys,email,email.policy,concurrent.futures
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003')
mode=sys.argv[1];assert mode in ['candidate','live']
names=sys.argv[2:];assert all(n in ['terry','amanda','edith','gohzed','grogar','inga','maggie','marsha','victor','vivian','wilma'] for n in names)
def test(n):
 base=['docker','exec',n]+(['himalaya'] if mode=='live' else ['/tmp/cody-himalaya-v2','-c','/tmp/cody-himalaya-v2.toml'])
 def run(*args):
  p=subprocess.run(base+list(args),capture_output=True,timeout=60)
  if p.returncode:raise RuntimeError(n+': '+str(args[:2])+' exited '+str(p.returncode))
  return p.stdout
 c=json.loads(subprocess.check_output(['docker','inspect',n]))[0];env=dict(x.split('=',1) for x in c['Config']['Env'])
 result={'agent':n,'mode':mode,'version':run('--version').decode().splitlines()[0]}
 check=run('account','check').decode();result['imapAuth']='imap: OK' in check;result['smtpAuth']='smtp: OK' in check;assert result['imapAuth'] and result['smtpAuth'],n+' account check failed'
 boxes=json.loads(run('mailbox','list','--json'));boxes=boxes.get('mailboxes',boxes) if isinstance(boxes,dict) else boxes;result['mailboxCount']=len(boxes)
 messages=json.loads(run('envelope','list','--mailbox','INBOX','--page-size','2','--json'))['envelopes'];result['envelopesReturned']=len(messages)
 if messages:
  msg=messages[0];mid=str(msg['id']);raw=run('message','read','--mailbox','INBOX',mid,'--raw');parsed=email.message_from_bytes(raw,policy=email.policy.default);assert parsed.keys();result['messageRead']=True
  after=json.loads(run('envelope','list','--mailbox','INBOX','--page-size','2','--json'))['envelopes'];match=next((x for x in after if str(x['id'])==mid),None)
  result['readFlagsUnchanged']=match is not None and match.get('flags')==msg.get('flags');assert result['readFlagsUnchanged']
 else:result['messageRead']='empty inbox'
 draft=run('message','compose','--to','maintenance-test@example.invalid','--subject','Unsent maintenance verification','--body','Local draft only. Do not send.')
 parsed=email.message_from_bytes(draft,policy=email.policy.default);assert email.utils.parseaddr(parsed['From'])[1]==env['EMAIL_ADDRESS'];assert email.utils.parseaddr(parsed['To'])[1]=='maintenance-test@example.invalid'
 assert 'Local draft only.' in parsed.get_body(preferencelist=('plain',)).get_content()
 result.update({'draftCompose':True,'senderMatchesConfiguredAccount':True,'sent':False,'savedToMailbox':False})
 (b/n/('verification-'+mode+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(test,names))
