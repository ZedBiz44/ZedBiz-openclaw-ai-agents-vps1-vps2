const fs=require('node:fs');
const file=process.argv[2];
let source=fs.readFileSync(file,'utf8');
const needle='\t\tconst preAbortActiveTaskIds = new Set(getCommandLaneActiveTaskIds(sessionLane));';
const guard=`\t\tif (activeSessionId || (activeWorkSessionId && isEmbeddedAgentRunActive(activeWorkSessionId)) ||
\t\t\t(sessionLane && getCommandLaneSnapshot(sessionLane).activeCount > 0)) {
\t\t\treturn reportRecoveryOutcome({
\t\t\t\tstatus: "skipped", action: "observe_only", reason: "active_work_no_elapsed_cutoff",
\t\t\t\tsessionId: params.sessionId, sessionKey: params.sessionKey,
\t\t\t\tactiveSessionId: activeSessionId ?? activeWorkSessionId
\t\t\t});
\t\t}
`;
if(!source.includes('active_work_no_elapsed_cutoff')) {
 if(source.split(needle).length!==2)throw Error('Unexpected upstream recovery structure');
 source=source.replace(needle,guard+needle);fs.writeFileSync(file,source);
}
if(source.indexOf('active_work_no_elapsed_cutoff')>source.indexOf(needle))throw Error('Guard order wrong');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const actual=source.slice(source.indexOf(guard.trimStart().slice(0,60)),source.indexOf(needle));
assert.ok(actual.includes('active_work_no_elapsed_cutoff'));
for(const row of [
 {activeSessionId:'live',activeWorkSessionId:null,laneCount:0,embedded:false,expected:'skipped'},
 {activeSessionId:null,activeWorkSessionId:'worker',laneCount:0,embedded:true,expected:'skipped'},
 {activeSessionId:null,activeWorkSessionId:null,laneCount:1,embedded:false,expected:'skipped'},
 {activeSessionId:null,activeWorkSessionId:'old',laneCount:0,embedded:false,expected:'continue'},
 {activeSessionId:null,activeWorkSessionId:null,laneCount:0,embedded:false,expected:'continue'}
]) {
 const result=vm.runInNewContext('(function(){'+actual+'return {status:"continue"};})()',{
  ...row,sessionLane:'test',params:{sessionId:'test',sessionKey:'test'},
  isEmbeddedAgentRunActive:()=>row.embedded,
  getCommandLaneSnapshot:()=>({activeCount:row.laneCount}),reportRecoveryOutcome:x=>x
 });
 assert.equal(result.status,row.expected);
}
console.log('Amanda live-owner protection preserved');
