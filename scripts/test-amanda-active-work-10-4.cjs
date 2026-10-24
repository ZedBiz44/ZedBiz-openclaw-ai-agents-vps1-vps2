const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2],'utf8').replace(/^import .*;\n/gm,'').replace(/^export .*;\n?/gm,'');
async function test(name,overrides,expected) {
 let resets=0,aborts=0;
 const ctx={Set,Date,Math,Error,String, diagnosticLogger:{warn(){}},formatRecoveryOutcome:JSON.stringify,
 resolveStuckSessionRecoveryRef:()=> 'main',isDiagnosticSessionStateCurrent:()=>true,
 recoverTerminalSessionPlacementTurn:async()=>undefined,isEmbeddedAgentRunHandleActive:()=>false,
 resolveActiveEmbeddedRunHandleSessionId:()=>undefined,resolveActiveEmbeddedRunSessionId:()=>undefined,
 isEmbeddedAgentRunActive:()=>false,prepareStaleFollowupDrainRetirement:()=>()=>{},resolveSessionLane:()=> 'lane',
 getCommandLaneSnapshot:()=>({activeCount:0,queuedCount:0}),getCommandLaneActiveTaskIds:()=>[],
 resolveEmbeddedReplyActivity:()=>undefined,resetCommandLane:()=>{resets++;return 0;},
 abortAndDrainEmbeddedAgentRun:()=>{aborts++;throw Error('Unexpected abort');},logWithSessionDiagnosticContext:()=>{},...overrides};
 vm.createContext(ctx);vm.runInContext(source,ctx);
 const result=await ctx.recoverStuckDiagnosticSession({sessionId:'test',sessionKey:'main',ageMs:86400000,allowActiveAbort:true,queueDepth:4});
 assert.equal(result.reason,expected,name);assert.equal(aborts,0,name);if(expected!=='no_active_work')assert.equal(resets,0,name);
 console.log(name+': PASS');
}
(async()=>{
 await test('Live handle', {resolveActiveEmbeddedRunHandleSessionId:()=> 'active'},'active_work_no_elapsed_cutoff');
 await test('Live embedded run',{isEmbeddedAgentRunActive:()=>true},'active_work_no_elapsed_cutoff');
 await test('Live lane',{getCommandLaneSnapshot:()=>({activeCount:1,queuedCount:4})},'active_work_no_elapsed_cutoff');
 await test('Stale generation',{isDiagnosticSessionStateCurrent:()=>false},'stale_session_state');
 await test('Terminal worker still handled',{recoverTerminalSessionPlacementTurn:async()=> 'failed worker'},'terminal_worker');
 await test('Ownerless stale session still released',{},'no_active_work');
})().catch(e=>{console.error(e);process.exitCode=1});
