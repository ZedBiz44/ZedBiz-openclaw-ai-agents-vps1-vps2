import {Client} from '/app/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StreamableHTTPClientTransport} from '/app/node_modules/@modelcontextprotocol/sdk/dist/esm/client/streamableHttp.js';
import assert from 'node:assert/strict';
const client=new Client({name:'cody-recovery-readonly-proof',version:'1.0'});
const transport=new StreamableHTTPClientTransport(new URL('http://127.0.0.1:8080/mcp'),{requestInit:{headers:{Authorization:`Bearer ${process.env.MCP_AUTH_TOKEN}`}}});
await client.connect(transport);
try{
 const list=await client.listTools();assert.equal(list.tools.length,126);
 for(const name of ['asana_create_task','asana_update_task','asana_create_subtask'])assert.equal(list.tools.find(t=>t.name===name)?.inputSchema.properties.is_rendered_as_separator.type,'boolean');
 const response=await client.callTool({name:'asana_get_user',arguments:{user_gid:'me'}});
 assert(!response.isError,'Identity read failed');
 const text=response.content.filter(x=>x.type==='text').map(x=>x.text).join('\n');
 assert(text.includes('1213974002925107'),'Unexpected Asana identity');
 console.log(JSON.stringify({ok:true,tools:126,nativeHeadingSchemas:3,identityGid:'1213974002925107',externalWrites:0}));
}finally{await transport.terminateSession();await client.close();}
