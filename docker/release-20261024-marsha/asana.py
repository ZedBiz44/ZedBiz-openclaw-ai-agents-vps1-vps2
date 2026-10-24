"""Compare live and isolated candidate Asana catalogs and own-user reads."""
import json,os,pathlib,subprocess,time
os.umask(0o077)
root=pathlib.Path('/opt/openclaw/backups/release-20261024-marsha/asana-pilot');root.mkdir(mode=0o700,exist_ok=True)
js="""import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StreamableHTTPClientTransport} from '@modelcontextprotocol/sdk/client/streamableHttp.js';
const c=new Client({name:'cody-readonly-release-proof',version:'1.0'});
await c.connect(new StreamableHTTPClientTransport(new URL('http://127.0.0.1:8080/mcp'),{requestInit:{headers:{Authorization:'Bearer '+process.env.MCP_AUTH_TOKEN}}}));
console.log(JSON.stringify({tools:(await c.listTools()).tools.map(t=>({name:t.name,inputSchema:t.inputSchema})).sort((a,b)=>a.name.localeCompare(b.name)),identity:await c.callTool({name:'asana_get_user',arguments:{user_gid:'me'}})}));await c.close();"""
results=[]
for name in ['marsha']:
 work=root/name;work.mkdir(mode=0o700)
 live=name+'-asana-mcp';pilot='cody-20261024-asana-'+name
 d=json.loads(subprocess.check_output(['docker','inspect',live]))[0]
 assert not d['Mounts'],'Review sidecar mounts before reproduction'
 (work/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n')
 def probe(container,label):
  p=subprocess.run(['docker','exec',container,'node','--input-type=module','-e',js],capture_output=True,text=True,timeout=120)
  (work/(label+'.log')).write_text(p.stdout+p.stderr)
  assert p.returncode==0,'Read-only Asana probe failed; private log retained'
  o=json.loads(p.stdout);assert not o['identity'].get('isError');return o
 before=probe(live,'before')
 image='zedbiz/asana-http-mcp:2.0.0-'+('edith-' if name=='edith' else '')+'components-20261023'
 try:
  subprocess.run(['docker','run','-d','--name',pilot,'--network','openclaw','--memory','512m','--env-file',str(work/'runtime.env'),image,*d['Config']['Cmd']],stdout=subprocess.DEVNULL,check=True)
  for _ in range(30):
   current=json.loads(subprocess.check_output(['docker','inspect',pilot]))[0]
   assert current['State']['Running'],'Candidate sidecar exited'
   if current['State'].get('Health',{}).get('Status')=='healthy':break
   time.sleep(2)
  else:raise RuntimeError('Candidate readiness failed')
  after=probe(pilot,'after');assert before==after,'Catalog schemas or own-user result changed'
  node=subprocess.check_output(['docker','exec',pilot,'node','--version'],text=True).strip();assert node=='v24.22.1'
  result={'agent':name,'image':image,'imageId':current['Image'],'node':node,'toolCount':len(after['tools']),'catalogSchemasAndIdentityMatch':True,'readOnly':True}
  (work/'acceptance.json').write_text(json.dumps(result,indent=2));results.append(result);print(json.dumps(result),flush=True)
 finally:
  if subprocess.run(['docker','inspect',pilot],capture_output=True).returncode==0:
   subprocess.run(['docker','stop',pilot],stdout=subprocess.DEVNULL,check=True)
   subprocess.run(['docker','rm',pilot],stdout=subprocess.DEVNULL,check=True)
(root/'acceptance.json').write_text(json.dumps(results,indent=2))


