import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
// Usage: node call.mjs request.json [launch-script]; request has name and arguments.
const [requestPath,entry]=process.argv.slice(2);
const req=JSON.parse(readFileSync(requestPath,'utf8'));
if(!['analyze_media_file','analyze_youtube_video'].includes(req.name))throw new Error('Unsupported tool');
const client=new Client({name:'zedbiz-media-cli',version:'0.2.0'});
try {
 await client.connect(new StdioClientTransport({command:process.execPath,args:[entry||fileURLToPath(new URL('./launch-cody.mjs',import.meta.url))],env:process.env,stderr:'inherit'}));
 const result=await client.callTool(req,undefined,{timeout:600000});
 console.log(JSON.stringify(result,null,2));if(result.isError)process.exitCode=1;
} finally {await client.close();}
