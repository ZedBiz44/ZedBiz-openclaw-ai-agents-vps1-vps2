import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {analyzeMedia,inspectMedia} from '../media.mjs';
test('reject unsupported/nonabsolute inputs before upload', async()=>{
  await assert.rejects(inspectMedia('relative.mp4'),/absolute/);
  await assert.rejects(inspectMedia(join(tmpdir(),'credentials.json')),/Unsupported/);
});
test('file analysis includes audio-bearing video, explicit sampling and deletes upload',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'gemini-test-')); const file=join(dir,'test.mp4'); await writeFile(file,'test');
  let request,deleted=0;
  const client={files:{upload:async()=>({name:'files/test',uri:'https://example.test/video',state:'ACTIVE'}),delete:async()=>{deleted++;}},interactions:{create:async x=>{request=x;return {output_text:'The speaker says hello.',usage:{total_tokens:4}};}}};
  try {const result=await analyzeMedia(client,'test-model',{file_path:file,fps:12,start_seconds:1,end_seconds:3});assert.equal(request.store,false);assert.deepEqual(request.input[1].processing,{type:'static',fps:12,start_offset:1,end_offset:3});assert.equal(deleted,1);assert.equal(result.uploaded_file_cleanup,'deleted');
    let submits=0;client.interactions.create=async()=>{submits++;throw new Error('timeout');}; await assert.rejects(analyzeMedia(client,'test',{file_path:file}),/do not retry automatically/);assert.equal(submits,1);assert.equal(deleted,2);
  } finally {await rm(dir,{recursive:true,force:true});}
});
