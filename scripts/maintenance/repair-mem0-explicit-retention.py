#!/usr/bin/env python3
"""Version-gated Mem0 1.1.0/1.2.1 repair: preserve explicit facts and expose unique recall tools."""
import argparse,hashlib,json,os,pathlib,tempfile

OLD='''        const combinedText = allFacts.join("\\n");
        const result = await provider.add([{ role: "user", content: combinedText }], buildAddOptions(uid, runId, currentSessionId));'''
NEW='''        const combinedText = allFacts.join("\\n");
        // ZedBiz explicit retention: the agent already selected and sanitized these facts.
        // Keep automatic capture's extraction path unchanged.
        const explicitOptions = {
          ...buildAddOptions(uid, runId, currentSessionId),
          infer: false,
          deduced_memories: allFacts,
          metadata: {
            ...(p.metadata ?? {}),
            ...(p.category && { category: p.category }),
            ...(p.importance !== undefined && { importance: p.importance })
          }
        };
        const result = await provider.add([{ role: "user", content: combinedText }], explicitOptions);'''
OLD_REGISTER='''  api.registerTool(createMemorySearchTool(deps), nonOptional);'''
NEW_REGISTER='''  api.registerTool({ ...createMemorySearchTool(deps), name: "mem0_search", label: "Mem0 Search" }, nonOptional);
  api.registerTool({ ...createMemoryGetTool(deps), name: "mem0_get", label: "Mem0 Get" }, nonOptional);
  api.registerTool(createMemorySearchTool(deps), nonOptional);'''

def transform(text):
    if NEW not in text:
        if text.count(OLD)!=1:raise ValueError('Unrecognized explicit-add implementation; refusing patch')
        text=text.replace(OLD,NEW)
    if NEW_REGISTER not in text:
        if text.count(OLD_REGISTER)!=1:raise ValueError('Unrecognized registration; refusing patch')
        text=text.replace(OLD_REGISTER,NEW_REGISTER)
    old_receipt='`[${r.event}] ${r.memory}`'
    new_receipt='`[${r.event}] id=${r.id ?? "unavailable"} ${r.memory}`'
    if old_receipt in text:text=text.replace(old_receipt,new_receipt)
    elif new_receipt not in text:raise ValueError('Unrecognized memory receipt')
    old_limit='top_k: limit ?? cfg.topK,'
    new_limit='top_k: limit ?? Math.max(cfg.topK ?? 5, 20),'
    if old_limit in text:text=text.replace(old_limit,new_limit)
    elif new_limit not in text:raise ValueError('Unrecognized explicit search limit')
    return text

def main():
    ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    root=pathlib.Path(args.project)/'node_modules/@mem0/openclaw-mem0'
    if json.loads((root/'package.json').read_text())['version'] not in ('1.1.0','1.2.1'):raise SystemExit('Only versions 1.1.0 and 1.2.1 are approved')
    target=root/'dist/index.js';old=target.read_bytes();new=transform(old.decode()).encode();stat=target.stat()
    manifest=root/'openclaw.plugin.json';manifest_old=manifest.read_bytes();data=json.loads(manifest_old)
    names=data.get('contracts',{}).get('tools')
    if not isinstance(names,list) or not {'memory_search','memory_get'}.issubset(names):raise SystemExit('Unrecognized tool contract')
    for alias in ['mem0_search','mem0_get']:
        if alias not in names:names.append(alias)
    manifest_new=(json.dumps(data,indent=2)+'\n').encode()
    if args.check:print(json.dumps({'valid':True,'already_applied':old==new and manifest_old==manifest_new}));return
    if old!=new:
        backup=target.with_name('index.js.before-zedbiz-retention-20260927')
        if not backup.exists():backup.write_bytes(old);os.chmod(backup,stat.st_mode & 0o777)
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as f:f.write(new);temp=f.name
        os.chmod(temp,stat.st_mode & 0o777);os.chown(temp,stat.st_uid,stat.st_gid)
        if target.read_bytes()!=old:raise RuntimeError('Concurrent plugin change')
        os.replace(temp,target)
    if manifest_old!=manifest_new:
        ms=manifest.stat();mb=manifest.with_name('openclaw.plugin.json.before-zedbiz-retention-20260927')
        if not mb.exists():mb.write_bytes(manifest_old);os.chmod(mb,ms.st_mode & 0o777)
        with tempfile.NamedTemporaryFile(dir=manifest.parent,delete=False) as f:f.write(manifest_new);temp=f.name
        os.chmod(temp,ms.st_mode & 0o777);os.chown(temp,ms.st_uid,ms.st_gid)
        if manifest.read_bytes()!=manifest_old:raise RuntimeError('Concurrent manifest change')
        os.replace(temp,manifest)
    print(json.dumps({'path':str(target),'sha':hashlib.sha256(new).hexdigest(),'changed':old!=new}))

if __name__=='__main__':main()
