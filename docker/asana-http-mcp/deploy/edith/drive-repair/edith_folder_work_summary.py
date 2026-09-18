"""Compact progress and pre-task workload assessment from a saved full inventory."""
import collections
import json
import sys
from pathlib import Path, PurePosixPath

def assess(inventory):
    assert inventory.get('complete') is True, 'Complete paginated inventory required'
    groups = {}
    for item in inventory['items']:
        if item.get('mimeType') == 'application/vnd.google-apps.folder':
            continue
        path = PurePosixPath(item.get('path') or item['name'])
        group = path.parts[0] if len(path.parts) > 1 else '(root files)'
        row = groups.setdefault(group, {'files':0,'bytes':0,'types':{},'unique_binary_contents':set(),'without_checksum':0})
        ext=path.suffix.lower() or '(no extension)'
        row['files']+=1;row['bytes']+=int(item.get('size') or 0)
        row['types'][ext]=row['types'].get(ext,0)+1
        if item.get('md5Checksum'):row['unique_binary_contents'].add((item['md5Checksum'],str(item.get('size'))))
        else:row['without_checksum']+=1
    for row in groups.values():row['unique_binary_contents']=len(row['unique_binary_contents'])
    return {'groups':groups,'planning_rule':'Compare unique contents, file types, natural subfolders, and needed judgment before creating tasks. Keep normal folders as one assignment. Split unusually large or mixed folders by coherent purpose or existing subfolder with distinct source IDs, one parent and one final reconciliation. File count alone does not determine effort; preserved Photoshop/package contents need less judgment. No timer-derived splits.'}

def summary(base):
    base=Path(base)
    out=assess(json.loads((base/'initial-inventory.json').read_text()))
    if (base/'execution-state.json').exists():
        state=json.loads((base/'execution-state.json').read_text())
        out['progress']={'source_copy_proofs':len(state.get('copies',{})),
            'unique_active_files':len({x['active_id'] for x in state.get('copies',{}).values()}),
            'archived_originals':len(state.get('archived',[])),
            'pending_copy_proofs':len(state.get('pending',{}))}
        # Counts are progress, never a completion or reviewer-acceptance verdict.
    return out

if __name__=='__main__':print(json.dumps(summary(sys.argv[1]),indent=2))

