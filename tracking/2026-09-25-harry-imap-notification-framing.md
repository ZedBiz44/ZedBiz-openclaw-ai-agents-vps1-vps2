# Harry IMAP assignment recovery

Date: 2026-09-25 MDT | Operator: Cody | Scope: Harry only

## Problem and authorization
Jack authorized immediate repair after the existing Asana assignment email reached Harry but produced only a summary. The installed IMAP renderer imposed summary-only framing despite Harry's existing approved email task rules. Terry had already completed his task and was not replayed or modified.

## Runtime changes
- Exact-match renderer patch: `/opt/openclaw-harry/node_modules/openclaw/dist/extensions/imap/index.js`.
- Added `/opt/openclaw-harry/patch-imap-notification-framing.py` and its test script.
- Added an invocation of the patcher immediately before `exec op run` in `/opt/openclaw-harry/start-harry.sh`, preserving the protected 1Password startup path.
- Changed only `plugins.entries.imap.config.accounts.agent_mail.timeoutSeconds` from 120 to 600 in `/root/.openclaw-harry/openclaw.json`.
- Backup suffix for bundle, startup script and configuration: `.before-notification-framing-20260925`.
- Patched bundle SHA-256: `baa565e1404898fe026f26027d84e66204163f6db639859681fef2d0d2190c43`.
- Sender allowlist, verified-sender requirement, untrusted-content wrapping, UID claims and metadata-first download correction were preserved. No AGENTS.md or maintained Notion prompt was changed.

## Verification
Three patcher tests passed: isolated replacement, idempotent reapplication, and fail-closed unknown/ambiguous code. Node syntax check passed. Existing sweep regression tests passed quiet inbox, empty inbox, UID gaps/new messages and retry cursor retention.

Protected systemd restart returned to active/running with zero automatic restarts. The gateway became ready at 15:41:54 and IMAP push mode reconnected at 15:41:55. The previous process drained active work but did not fully exit before the systemd stop timeout; systemd terminated it and launched the new process. First test submission failed with ECONNREFUSED while the gateway was still starting; no job was created then.

At 15:42:10 a single approved recovery job replayed the original received assignment payload through `mail_reader`, retaining its external-untrusted wrapper and replacing only the obsolete renderer sentence with the deployed neutral notification framing. This tests downstream processing of an already-received notification; it is not a newly sent email or a fresh SMTP/IMAP transport test. Original receipt was independently verified earlier.

Harry verified his own Asana identity, fetched task `1218880903607195`, posted snapshot comment `1218881361762580` at 15:43:31, and completed the task at 15:43:32. Cody's independent Asana read confirms the snapshot authored by Harry and `completed=true`. No duplicate task was created. Test job: `edb23add-2cf8-4a32-82a2-f6b3e2679f33` with delete-after-run and no fallback delivery.

## Remaining limits and recovery
Harry reported a memory lookup timeout and incomplete Notion/Wiki capture; these do not invalidate the saved Asana deliverable. No fleet-wide fix is claimed. The patcher guards ordinary startup; an upstream update with different renderer code requires review instead of forced patching.

Rollback: restore the three matching backups and use the same protected systemd restart. Restoring the startup script removes automatic patch application. Do not replay the now-completed Asana task.

Local git push failed due to unavailable HTTPS authentication. Source and tests were published through the connected GitHub app. PR #404 is open; main does not yet contain this change. Evidence: issue #252.
