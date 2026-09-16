# Victor Workshop change reviews

Victor owns a read-only follow-up review 30 minutes after each OpenClaw main agent's weekly Skill Workshop cleanup. The follow-up is silent when the Workshop folder did not change. When a file was added, changed, or deleted, Victor compares the change with that agent's workspace skills and reports to Discord channel `1546640814573101128`.

## Authoritative locations

- VPS1 Workshop example: `/opt/openclaw/agents/amanda/agents/main/agent/workshop-skills`
- VPS1 workspace skills example: `/opt/openclaw/agents/amanda/workspace/skills`
- VPS2 Workshop: `/root/.openclaw-<agent>/agents/main/agent/workshop-skills`
- VPS2 workspace skills: `/root/.openclaw-<agent>/workspace/skills`
- VPS4 Workshop: `/home/openclaw/.openclaw/agents/main/agent/workshop-skills`
- VPS4 workspace skills: `/home/openclaw/.openclaw/workspace/skills`

## Safety

- The scanner only reads files and stores hashes in Victor's private state directory.
- Remote access uses a dedicated SSH key with a forced command. It cannot start a shell, forward ports, or read outside the configured Workshop and workspace-skill folders.
- Victor's report prompt forbids editing either skill collection.
- Existing files are baselined at deployment so old skills are not reported as newly created.
- Roll back by disabling or removing only cron jobs whose declaration key begins `zedbiz:workshop-change-review:` and removing the dedicated restricted SSH key entries.

## Report behavior

The scheduled job runs `workshop_change.py check --agent <name>`. `NO_CHANGE` produces `NO_REPLY`. A change packet includes added, changed, and deleted paths, the changed Workshop text, and the names and descriptions of the agent's workspace skills. Victor reads a related workspace `SKILL.md` only when the index suggests a possible overlap.

Victor reports:

- what changed;
- which workspace skills are related;
- whether the change supports, overlaps, or conflicts with them;
- what Jack should review next;
- confirmation that no files were changed.

## Main-review and Victor schedules

All times are Mountain Time. The OpenClaw job is system-owned and repeats every seven days. Victor runs exactly 30 minutes later.

| Agent | OpenClaw main review | Victor change review |
|---|---:|---:|
| Amanda | Sunday 23:15 | Sunday 23:45 |
| Edith | Friday 15:47 | Friday 16:17 |
| GoZed | Tuesday 17:38 | Tuesday 18:08 |
| Grogar | Thursday 18:35 | Thursday 19:05 |
| Inga | Wednesday 07:53 | Wednesday 08:23 |
| Maggie | Tuesday 00:29 | Tuesday 00:59 |
| Marsha | Sunday 19:08 | Sunday 19:38 |
| Terry | Saturday 16:21 | Saturday 16:51 |
| Victor | Wednesday 18:12 | Wednesday 18:42 |
| Vivian | Friday 09:42 | Friday 10:12 |
| Wilma | Saturday 04:45 | Saturday 05:15 |
| Harry | Wednesday 09:58 | Wednesday 10:28 |
| Suzy | Monday 10:29 | Monday 10:59 |
| Frank | Wednesday 18:36 | Wednesday 19:06 |
| Rocky | Monday 18:39 | Monday 19:09 |

OpenClaw creates a separate weekly review for the `mail_reader` identity when that identity exists. Stock `auto` mode does not provide a supported switch to keep the main review automatic while disabling only the mail-reader review.

Run tests with `python3 -m unittest -v` in this directory.
