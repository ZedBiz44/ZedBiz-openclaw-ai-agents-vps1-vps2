import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import plugin,{createProvider,mem0ConfigSchema} from './mem0-candidate/node_modules/@mem0/openclaw-mem0/dist/index.js';
function resolve(v){
 if(typeof v==='string')return v.replace(/\$\{([^}]+)\}/g,(_,k)=>{assert(process.env[k],`Missing env ${k}`);return process.env[k]});
 if(v && typeof v==='object'){
  if(v.source==='env' && v.id){assert(process.env[v.id],`Missing env ${v.id}`);return process.env[v.id]}
  return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,resolve(x)]));
 }
 return v;
}
const cfg=resolve(JSON.parse(fs.readFileSync('/root/.openclaw-harry/openclaw.json')).plugins.entries['openclaw-mem0'].config);
const tools=new Map();const api={pluginConfig:{...cfg,autoCapture:false,autoRecall:false},resolvePath:p=>path.resolve(p),logger:{info(){},warn(){},error(){},debug(){}},registerTool:t=>tools.set(t.name,t),registerCli(){},registerService(){},on(){}};
plugin.register(api);
assert(tools.has('mem0_search') && tools.has('mem0_get'));
const provider=createProvider(mem0ConfigSchema.parse(cfg),api);
const found=await provider.search('ZedBiz',{user_id:cfg.userId,top_k:5,threshold:0.1});assert(found.length>0);
const uid='cody-upgrade-test-'+randomUUID();const fact='Maintenance verification marker '+randomUUID()+' belongs only to a temporary isolated test account.';
let ids=[];
try{
 const added=await tools.get('memory_add').execute('test-add',{facts:[fact],userId:uid,metadata:{maintenanceTest:true},category:'technical'});
 assert(!added.details?.error,JSON.stringify(added.details));
 const stored=await provider.getAll({user_id:uid});ids=stored.map(m=>m.id);assert(ids.length===1);assert.equal(stored[0].memory,fact);
 const get=await tools.get('mem0_get').execute('test-get',{memoryId:ids[0]});assert(!get.details?.error,JSON.stringify(get.details));
 console.log(JSON.stringify({existingRecallCount:found.length,explicitFactPreserved:true,aliasesAvailable:true,version:'1.2.1',temporaryMemoryCount:ids.length}));
}finally{
 if(!ids.length)ids=(await provider.getAll({user_id:uid})).map(m=>m.id);
 for(const id of ids)await provider.delete(id);
 assert.equal((await provider.getAll({user_id:uid})).length,0);console.log('TEMPORARY_MEMORY_REMOVED');
}
process.exit(0);
