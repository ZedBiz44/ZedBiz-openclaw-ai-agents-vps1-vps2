import json,os,subprocess,sys
image='zedbiz/openclaw-base:2026.9.8-terry-20261003-imapfix'
config=json.loads(subprocess.check_output(['docker','inspect','terry']))[0]
env=os.environ.copy()
args=['docker','run','--rm','--network','openclaw','--volumes-from','terry','--user','node']
for item in config['Config']['Env']:
 key,value=item.split('=',1)
 if key in ('PATH','NODE_VERSION','YARN_VERSION'):continue
 env[key]=value
 args+=['-e',key]
args+=['--entrypoint','openclaw',image,*sys.argv[1:]]
raise SystemExit(subprocess.call(args,env=env))
