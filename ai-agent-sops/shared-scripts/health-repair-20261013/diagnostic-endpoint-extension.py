
def extra_diagnostics(profile, agent, root):
    result = {}
    if agent in ('frank','harry','suzy'):
        unit = 'openclaw-' + agent + '.service'
        result['unitMemory'] = command(['systemctl','show',unit,'--property=MemoryMax,MemoryHigh,MemorySwapMax,ControlGroup,ActiveState,MainPID'])
        result['memoryDropIns'] = []
        for base in ['/etc/systemd/system','/etc/systemd/system.control','/run/systemd/system.control']:
            for p in (Path(base)/(unit+'.d')).glob('*.conf'):
                lines = [line for line in p.read_text().splitlines() if line.strip().startswith(('MemoryMax=','MemoryHigh=','MemorySwapMax='))]
                if lines: result['memoryDropIns'].append({'path':str(p),'settings':lines,'modifiedAtUnix':p.stat().st_mtime})
        cg = Path('/sys/fs/cgroup/system.slice')/unit
        result['liveMemory'] = {name:(cg/name).read_text().strip() for name in ('memory.max','memory.high','memory.current','memory.swap.current')}
    if agent == 'rocky':
        with sqlite3.connect('file:'+str(root/'state/openclaw.sqlite')+'?mode=ro',uri=True) as c:
            c.row_factory=sqlite3.Row
            result['diagnosticIdentities']=[dict(r) for r in c.execute('SELECT identity_key,device_id,updated_at_ms FROM device_identities')]
            result['deviceGrants']=[dict(r) for r in c.execute('SELECT device_id,role,scopes_json,updated_at_ms FROM device_auth_tokens')]
            result['pairedScopes']=[dict(r) for r in c.execute('SELECT device_id,display_name,client_id,client_mode,role,roles_json,scopes_json,approved_scopes_json,approved_at_ms FROM device_pairing_paired')]
    if agent == 'ruby':
        code = "import sys,json,importlib.metadata as m;print(json.dumps({'executable':sys.executable,'python':sys.version,'packages':sorted([{'name':d.metadata['Name'],'version':d.version} for d in m.distributions()],key=lambda x:x['name'].lower())}))"
        result['selectedPythonPackages'] = command(['docker','exec','hermes-ruby','/opt/hermes/.venv/bin/python','-c',code])
        result['auditEvidenceStatus'] = 'Installed inventory only; not a complete vulnerability audit.'
    return result

