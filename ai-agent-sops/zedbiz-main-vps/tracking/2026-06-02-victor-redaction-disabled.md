# 2026-06-02 - Victor Redaction Disabled

## Summary

- **Date:** 2026-06-02 Mountain Time
- **Changed By:** Codex
- **VPS:** VPS1 / main-vps `187.77.210.223`
- **Affected Agent:** Victor
- **Status:** done

## Business Reason

Jack asked for Victor to stop redacting owner-requested gateway tokens and tokenized login links. The immediate business requirement was to remove friction when Jack asks Victor for server access details.

## Change Made

Set Victor's OpenClaw logging redaction mode to `off`:

```bash
openclaw config set logging.redactSensitive off
```

Then restarted only the `victor` container.

## Verification

- Backup created before change:
  - `/home/node/.openclaw/openclaw.json.bak-redaction-off-20260602T182743Z`
- Victor config value after change:
  - `logging.redactSensitive = off`
- Victor container restart completed.
- Victor health after restart:
  - `healthy`
- Victor runtime:
  - user: `node`
  - home: `/home/node`
  - image: `zedbiz-openclaw-victor:2026.5.28-ssh`

## Risk

With `logging.redactSensitive` set to `off`, Victor may show sensitive values in tool output, transcripts, or diagnostics that would previously have been masked.

This is intentional for Victor because Jack wants owner-requested keys shown instead of redacted.

## Rollback

To turn redaction back on:

```bash
docker exec victor openclaw config set logging.redactSensitive tools
docker restart victor
```
