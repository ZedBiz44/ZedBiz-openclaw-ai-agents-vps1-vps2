"""Run a reviewed folder phase continuously; no LLM, timer, task creation or retry loop."""
from pathlib import Path, PurePosixPath
import fcntl, importlib.util, json, sys
from edith_folder_work_summary import pending_rows

BASE=Path('/home/node/.openclaw/private/folder-cleanup/laughs-and-fun')

def execute(module, phase):
    assert phase in ('exports','photoshop')
    m=module
    rows=pending_rows(m.plan,m.state,photoshop=phase=='photoshop')
    full={r['source_id']:r for r in m.plan['file_plan']}
    result={'phase':phase,'started':m.now(),'selected':len(rows),'processed':0,
            'new_copies':0,'duplicate_sources':0,'archived':0,'status':'running','errors':[]}
    verified=set()
    for row in rows:
        fid=row['source_id'];cid=row.get('active_copy_source_id',fid)
        try:
            if fid in m.state['archived'] and fid in m.state['copies']:
                continue
            existed=cid in m.state['copies']
            proof=m.copyrow(full[cid])
            if not existed:
                result['new_copies']+=1
                verified.add(proof['active_id'])
            elif proof['active_id'] not in verified:
                active=m.get(proof['active_id'])
                expected=m.state['folders'][str(PurePosixPath(proof['path']).parent)]
                assert active.get('parents')==[expected] and active.get('driveId')==m.DRIVE and not active.get('trashed')
                assert active.get('name')==proof['name']
                assert all(active.get(k)==proof[k] for k in ('md5Checksum','size'))
                assert m.sig(m.gog('permissions',proof['active_id']))==m.sig(m.rp)
                verified.add(proof['active_id'])
            original_parent=str(PurePosixPath(m.orig[fid]['path']).parent)
            archive_path='ZVIM-Laughs-And-Fun-Archive/Originals'+('' if original_parent=='.' else '/'+original_parent)
            archive_id=m.folder(archive_path)
            was_archived=fid in m.state['archived']
            m.archive(fid,archive_id)
            result['archived']+=not was_archived
            if cid!=fid:
                own=m.state['copies'][fid]
                m.state.setdefault('duplicate_crosswalks',{})[fid]={
                    'canonical_source_id':cid,'active_id':proof['active_id'],
                    'archive_id':archive_id,'source_md5':own['md5Checksum'],'verified_at':m.now()}
                result['duplicate_sources']+=1
            result['processed']+=1
            m.state.setdefault('phase_execution',{})[phase]=dict(result)
            m.persist()
        except Exception as error:
            result['status']='blocked'
            result['errors'].append({'source_id':fid,'error':str(error),
                'next_action':'Inspect the recorded live outcome. Never blindly retry an uncertain write.'})
            break
    if result['status']=='running':result['status']='phase-complete'
    result['ended']=m.now()
    result['remaining_in_phase']=len(pending_rows(m.plan,m.state,photoshop=phase=='photoshop'))
    if result['remaining_in_phase'] and result['status']=='phase-complete':result['status']='incomplete'
    m.state.setdefault('phase_execution',{})[phase]=result
    m.persist()
    m.save('phase-'+phase+'-result.json',result)
    return result

def main():
    phase=sys.argv[1]
    with (BASE/'execution-loop.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        spec=importlib.util.spec_from_file_location('saved_plan_executor',BASE/'execute-pilot.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result=execute(module,phase)
        print(json.dumps(result,indent=2))
        return 0 if result['status']=='phase-complete' else 2

if __name__=='__main__':raise SystemExit(main())

