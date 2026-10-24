import {loadAuthProfileStoreForRuntime} from '/app/dist/plugin-sdk/agent-runtime.js';
import fs from 'node:fs';
const cfg=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json'));
console.log(JSON.stringify({stateDir:process.env.OPENCLAW_STATE_DIR,agentDir:process.env.OPENCLAW_AGENT_DIR,configPath:process.env.OPENCLAW_CONFIG_PATH}));
console.log(JSON.stringify({agentsList:cfg.agents?.list?.map(a=>({id:a.id,agentDir:a.agentDir,workspace:a.workspace})),entries:Object.entries(cfg.agents?.entries??{}).map(([id,a])=>({id,agentDir:a.agentDir,workspace:a.workspace}))}));
const store=await loadAuthProfileStoreForRuntime('/home/node/.openclaw/agents/main/agent');
console.log(JSON.stringify({profiles:Object.entries(store.profiles).map(([id,p])=>({id,type:p.type,provider:p.provider,hasAccess:Boolean(p.access),hasRefresh:Boolean(p.refresh),expires:p.expires}))}));
