"""Detect missed Ruby review releases during an already-awake Edith sitting."""
from datetime import datetime, timezone

RUBY = '1215900603267704'


def overdue_reviews(tasks, now=None):
    now = now or datetime.now(timezone.utc)
    overdue = []
    for task in tasks:
        name = task.get('name', '')
        if task.get('completed') or not name.startswith('[Ruby review]') or 'pilot' in name.lower():
            continue
        if (task.get('assignee') or {}).get('gid') not in (None, RUBY):
            continue
        if not task.get('due_at'):
            continue
        due = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00'))
        if (now - due).total_seconds() >= 1800:
            overdue.append(task)
    return sorted(overdue, key=lambda task: task['due_at'])
