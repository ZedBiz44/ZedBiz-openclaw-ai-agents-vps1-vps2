"""Apply the reviewed dynamic memory-limit fix and fail on unknown code."""
import pathlib,subprocess
root=pathlib.Path('/app/dist')
files=[p for p in root.glob('*.mjs') if 'options?.processMemoryLimitBytes ?? DEFAULT_PROCESS_MEMORY_LIMIT_BYTES' in p.read_text()]
assert len(files)==1,'Unexpected dynamic-memory patch target count'
subprocess.run(['node','/opt/zedbiz/patch-dynamic-memory-10-6.cjs',str(files[0])],check=True)
subprocess.run(['node','--check',str(files[0])],check=True)

