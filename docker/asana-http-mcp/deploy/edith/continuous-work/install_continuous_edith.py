"""Narrow, backed-up dispatcher/brief migration; leaves admission and locks intact."""
from pathlib import Path
import ast
import sys

def patch(source):
    assert 'from continuous_edith import run_continuous' not in source
    source = source.replace("INTAKE,20)", "INTAKE,55)")
    old = 'Work at most 12 minutes, reserve time to save evidence and report, and end before the 15-minute runtime limit.'
    assert old in source
    source = source.replace(old, 'Use up to 40 minutes of useful work before the 45-minute safety timeout. Checkpoint groups and continue; do not stop after a small batch. This task and session persist across normal turns.')
    old = 'Reconcile saved results first. Read outstanding Ruby changes-requested decisions and earlier assigned dispatch tasks; prioritize concrete corrections after a safe checkpoint and consume their exact scope without launching another writer. Then continue one bounded approved family. Only complete this dispatch sitting after saving an exact next action; folder parents remain incomplete until independent acceptance.'
    assert old in source
    source = source.replace(old, 'Resume the exact active checkpoint and changed inputs only. Continue across approved families in the same task/session. Do not reload older dispatches or retry known blocked corrections. Keep this dispatch open across checkpoints and normal turns. Complete it only when all production is submitted or no authorized work can proceed, with an exact saved reason. Folder parents still require Ruby acceptance. Release a newly ready Ruby review by running python3 /home/node/.openclaw/workspace/scripts/ready_review_handoff.py.')
    old = "def run(gid,fd):\n lock=os.fdopen(int(fd),'a+')"
    assert old in source
    new = "def run(gid,fd):\n if not json.loads((ROOT/(gid+'.json')).read_text()).get('pilot'):\n  from continuous_edith import run_continuous\n  return run_continuous(sys.modules[__name__],gid,fd)\n lock=os.fdopen(int(fd),'a+')"
    source = source.replace(old,new)
    ast.parse(source)
    return source

def install(root):
    p = root / 'edith-project-dispatch.py'
    source = p.read_text()
    new = patch(source)
    backup = p.with_name(p.name + '.before-continuous-20260917')
    assert not backup.exists(), 'Inspect prior migration before rerunning'
    backup.write_text(source)
    tmp = p.with_suffix('.continuous.tmp')
    tmp.write_text(new)
    tmp.replace(p)
    b = root / 'edith-recovery-work.md'
    original = b.read_text()
    b.with_name(b.name + '.before-continuous-20260917').write_text(original)
    start = original.index('## Short sittings and continuation')
    end = original.index('## Enforced execution boundary', start)
    replacement = '''## Continuous work and recovery — September 17
- Jack approved removing repeated 10–15 minute fresh-session restarts. Keep the SAME dispatch task open while useful approved work remains. The supervisor retains the same OpenClaw session across turns and the exclusive writer lock. Do not create new work-session tasks.
- Work through successive ready groups. Save a compact checkpoint after each group and continue immediately. Allow up to 40 minutes of useful work before the 45-minute turn safety timeout. This is a recovery ceiling, not a minimum runtime or reason to repeat checks.
- The supervisor renews ONE existing backup ticket to 55 minutes ahead before a turn. It is only for a genuine interruption. Do not expedite it on normal progress. A normal next turn needs no email, assignment or fresh context.
- Keep this dispatch incomplete across ordinary checkpoints and turn endings. Complete it only when all production has been submitted or no authorized work remains possible, after recording exact results/blockers. The supervisor then cancels the unused backup. Independent Ruby acceptance remains required for folder parents.
- Submit and release Ruby reviews as folders become ready using the existing ready_review_handoff helper; do not wait for the whole project. Check the helper CLI before invoking it. Continue unrelated production while Ruby reviews.
- Do not repeatedly read the whole project, accepted folders, prior dispatch tasks, unchanged skills or the memory bank. Resume current context and checkpoint; inspect changed inputs and files about to be changed. Never repeat uncertain writes, unchanged blocked renames or held document copies.
- Post parent updates for meaningful progress, blockers or submission. Save external memory at folder submission or a material decision, not at each checkpoint. An Asana or memory reporting failure must never repeat file operations.
- All existing file safeguards, protected areas, Photoshop/package preservation exceptions and independent review remain in force. No model or credential changes.

'''
    b.write_text(original[:start] + replacement + original[end:])
    print('Installed continuous worker hook and aligned brief; backups saved.')

if __name__ == '__main__': install(Path(sys.argv[1]))

