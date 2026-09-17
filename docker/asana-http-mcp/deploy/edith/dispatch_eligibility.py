"""Pure eligibility checks for the existing task-assignment workflow."""
from datetime import datetime, timezone


def eligible(task, owner, read_dependency, now=None):
    now = now or datetime.now(timezone.utc)
    if (task.get('assignee') or {}).get('gid') != owner:
        return 'wrong-assignee'
    if task.get('resource_subtype') != 'default_task':
        return 'not-a-work-sitting'
    if task.get('completed'):
        return 'already-completed'
    if task.get('due_at') and datetime.fromisoformat(task['due_at'].replace('Z','+00:00')) > now:
        return 'not-yet-due'
    for dependency in task.get('dependencies', []):
        item = read_dependency(dependency['gid'])
        if item.get('resource_subtype') == 'approval':
            if item.get('approval_status') != 'approved':
                return 'dependency-not-approved'
        elif not item.get('completed'):
            return 'dependency-incomplete'
    return 'eligible'
