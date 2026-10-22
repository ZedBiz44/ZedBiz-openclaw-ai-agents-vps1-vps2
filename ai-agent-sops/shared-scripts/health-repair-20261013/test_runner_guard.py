import importlib.util,subprocess,unittest.mock as mock
from pathlib import Path
p=Path(__file__).with_name('run-openclaw-checks.py')
spec=importlib.util.spec_from_file_location('runner',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sample(free):return lambda:{'currentBytes':1024**3-free,'workingBytes':1024**3-free,'limitBytes':1024**3}
with mock.patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{}','')) as run:
 rows=m.run_checks([('health',['node','/test/light-gateway-check.mjs','root','health']),('channels',['node','/test/light-gateway-check.mjs','root','channels']),('doctor',['openclaw','doctor'])],{},lambda rows:None,sample(256*1024**2))
 assert [r['execution'] for r in rows]==['completed','completed','not_checked'];assert run.call_count==2
 rows=m.run_checks([('health',['node','/test/light-gateway-check.mjs','root','health'])],{},lambda rows:None,sample(64*1024**2));assert rows[0]['execution']=='not_checked';assert run.call_count==2
print('Guard regression assertions passed.')
