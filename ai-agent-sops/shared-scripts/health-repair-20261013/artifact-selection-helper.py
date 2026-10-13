
def latest_artifacts(root):
    selected = {}
    errors = []
    paths = [p for p in (root/'workspace/artifacts/health-checks').glob('*.json') if p.resolve().is_relative_to(root)]
    for p in sorted(paths, key=lambda x:x.stat().st_mtime_ns, reverse=True):
        try:
            data = json.loads(p.read_text())
            kind = data.get('mode') if isinstance(data,dict) else None
            kind = kind if kind in ('daily','weekly') else 'other'
            if kind not in selected:selected[kind]={'path':str(p),'result':data}
            if len(selected)==3:break
        except (OSError,ValueError) as e:
            errors.append({'path':str(p),'error':str(e)})
    return list(selected.values()),errors

