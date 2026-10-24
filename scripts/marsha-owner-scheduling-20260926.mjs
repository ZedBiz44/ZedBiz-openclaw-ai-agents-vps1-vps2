// Marsha-only repair for OpenClaw 2026.9.4. Issue #406.
// Run with --check first. Apply requires --apply; originals are retained.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const root = process.env.OPENCLAW_PATCH_ROOT || '/app';
const backup = process.env.OPENCLAW_PATCH_BACKUP || '/home/node/.openclaw/backups/marsha-owner-scheduling-20260926';
const direct = 'agent:main:discord:direct:864290378395025478';
const sender = '864290378395025478';
const oldGate = '&& !params.senderId && params.inputProvenance';
const newGate = `&& (!params.senderId || (params.senderIsOwner === true && params.senderId === ${JSON.stringify(sender)} && params.sessionKey === ${JSON.stringify(direct)})) && params.inputProvenance`;
const binding = `\t// Preserve the admitted run across Codex app-server callback boundaries.\n\tconst admittedIdentity = params.admittedRunContext ? createAdmittedGatewayToolCallerIdentity({\n\t\tadmittedRunContext: params.admittedRunContext,\n\t\tagentId: input.sessionAgentId,\n\t\tsessionKey: params.sessionKey,\n\t\tapprovalSignals: [input.runAbortController.signal],\n\t\tturnSourceChannel: params.messageChannel ?? params.messageProvider,\n\t\tturnSourceTo: params.currentMessagingTarget ?? params.currentChannelId,\n\t\tturnSourceAccountId: params.agentAccountId,\n\t\tturnSourceThreadId: params.currentThreadTs\n\t}) : undefined;\n\treturn exposedTools.map(tool => wrapToolWithGatewayCallerIdentity(tool, admittedIdentity));`;
function replaceOnce(text, before, after) {
  assert.equal(text.split(before).length - 1, 1, `Expected exactly one match: ${before.slice(0,100)}`);
  return text.replace(before, after);
}
const runtimePath = 'dist/run-attempt-AFiJ58Kv.mjs';
const toolsPath = 'dist/dynamic-tools-B3iuVIOQ.mjs';
const helperPath = 'dist/onboarding-welcome-sFL8cIpf.mjs';
const helper = fs.readFileSync(path.join(root, helperPath), 'utf8');
// The gateway already runs helper work on this lane. Nested inference must
// not wait for the main lane occupied by the agent awaiting its answer.
const updatedHelper = replaceOnce(helper, '\t\tagentId: SYSTEM_AGENT_ID,\n\t\ttrigger: "manual",', '\t\tagentId: SYSTEM_AGENT_ID,\n\t\tlane: "system-agent",\n\t\ttrigger: "manual",');
const runtime = fs.readFileSync(path.join(root, runtimePath), 'utf8');
const dynamic = fs.readFileSync(path.join(root, toolsPath), 'utf8');
const updatedRuntime = replaceOnce(runtime, oldGate, newGate);
const updatedDynamic = 'import { t as createAdmittedGatewayToolCallerIdentity, s as wrapToolWithGatewayCallerIdentity } from "./gateway-caller-context-acHXj8We.mjs";\n' + replaceOnce(dynamic, '\treturn exposedTools;\n}', binding + '\n}');
// Exercise the actual patched predicate, not a separately reimplemented rule.
const start = updatedRuntime.indexOf('function canResolveScheduledConfiguredMcpCreatorAuthority(params)');
assert.ok(start >= 0);
const end = updatedRuntime.indexOf('\n}', start) + 2;
const predicate = vm.runInNewContext('(' + updatedRuntime.slice(start,end) + ')', {isIncognitoSessionKey: key => key?.includes('incognito')});
const base = {trigger:'user', connectionClass:'local-loopback', bindingKind:'session', bindingSessionKey:direct, sessionKey:direct, usesSupervisionConnection:false, preservesNativeModel:false, senderIsOwner:true, hasStaticConfiguredMcp:true};
assert.equal(predicate(base), true);
assert.equal(predicate({...base, senderId:sender}), true);
for (const bad of [{senderIsOwner:false}, {senderId:'someone-else'}, {sessionKey:'agent:main:discord:group:other'}, {inputProvenance:{}}, {trustedInternalHandoff:{}}, {spawnedBy:'other'}, {scheduledToolPolicy:{}}, {usesSupervisionConnection:true}, {trigger:'cron'}]) {
  assert.equal(predicate({...base,senderId:sender,...bad}), false, JSON.stringify(bad));
}
// Check binding construction retains lifecycle and caller data for every tool.
const controller = new AbortController();
const params = {admittedRunContext:{test:true},sessionKey:direct,messageChannel:'discord',currentChannelId:sender,agentAccountId:'default'};
let captured;
const wrap = vm.runInNewContext('(function(params,input,exposedTools){'+binding+'})', {
  createAdmittedGatewayToolCallerIdentity: p => (captured=p),
  wrapToolWithGatewayCallerIdentity: (tool,identity) => ({tool,identity})
});
const result = wrap(params,{sessionAgentId:'main',runAbortController:controller},[{name:'automations'},{name:'openclaw'}]);
assert.equal(result.length,2);
assert.equal(captured.admittedRunContext,params.admittedRunContext);
assert.equal(captured.approvalSignals[0],controller.signal);
assert.equal(captured.sessionKey,direct);
assert.equal(captured.turnSourceChannel,'discord');
const changes = [[runtimePath,runtime,updatedRuntime],[toolsPath,dynamic,updatedDynamic],[helperPath,helper,updatedHelper]];
console.log('PASS: owner Discord accepted; other senders, delegated/scheduled and wrong-session requests rejected; active-run binding retained.');
if (process.argv.includes('--apply')) {
  assert.ok(!fs.existsSync(path.join(backup,'manifest.json')), 'Existing backup: inspect before reapplying');
  fs.mkdirSync(backup,{recursive:true});
  const manifest=[];
  for(const [file,before,after] of changes){
    const saved=path.join(backup,path.basename(file));
    fs.writeFileSync(saved,before);
    manifest.push({file,backup:saved,before:crypto.createHash('sha256').update(before).digest('hex'),after:crypto.createHash('sha256').update(after).digest('hex')});
  }
  fs.writeFileSync(path.join(backup,'manifest.json'),JSON.stringify(manifest,null,2));
  for(const [file,,after] of changes) fs.writeFileSync(path.join(root,file),after);
  console.log('Applied Marsha-only runtime patch. Backup: '+backup);
} else {
  console.log('Check only; no files changed.');
}
