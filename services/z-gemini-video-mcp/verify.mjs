import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
const [entry,file]=process.argv.slice(2);
const client=new Client({name:'zedbiz-video-verification',version:'1.0.0'});
const transport=new StdioClientTransport({command:process.execPath,args:[entry],env:process.env,stderr:'inherit'});
try {
 await client.connect(transport);
 const tools=await client.listTools(); console.log(JSON.stringify({tools:tools.tools.map(t=>t.name)}));
 if(!tools.tools.some(t=>t.name==='analyze_media_file')) throw new Error('Missing file-analysis tool');
 if(file){const result=await client.callTool({name:'analyze_media_file',arguments:{file_path:file,question:'Describe the visible colours and shapes in time order, and transcribe exactly the spoken words. Do not infer the speech from visible text. Brief answer.',fps:4}},undefined,{timeout:240000});console.log(JSON.stringify(result));if(result.isError)process.exitCode=1;}
} finally {await client.close();}
