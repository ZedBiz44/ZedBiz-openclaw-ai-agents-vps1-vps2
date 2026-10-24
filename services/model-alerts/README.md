# Primary model alerts

Independent Python standard-library monitor for VPS1 and VPS2. No AI generation or token refresh is required to send alerts. Tracks issue #295.

## Live deployment

- VPS1: `/home/jackadmin/model-alerts`, jackadmin crontab, 11 Docker agents: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, Wilma.
- VPS2: `/opt/zedbiz-model-alerts`, root crontab, three systemd agents: Harry, Suzy, Frank.
- Discord destination: `agent-health-report`, channel `1546640814573101128`. Alerts explicitly mention Jack (`864290378395025478`). Device notifications depend on Discord settings.
- Each host runs once per minute, using a nonblocking process lock. Output goes to system logging under `zedbiz-model-alerts`.
- Host-local `config.json` contains mode, host, agent state roots, channel ID, mention users, and the existing Marsha/Harry Discord bot token. Directory permissions are 0700 and configuration/state permissions are 0600. Never commit these files.

## Behavior

Reads the configured primary model, recent fallback decisions in gateway logs, and successful assistant replies in the actual agent SQLite store. Sends one failure notice per incident, including observed backup use if available. Repeated failures are quiet. Recovery requires a successful reply from the primary model and at least two minutes since the latest observed failure.

Every five minutes, a read-only Codex models request additionally checks each OpenAI OAuth credential. Confirmed `token_revoked` raises an alert. An accepted credential alone does not prove model recovery. Expired credentials and inconclusive probe failures do not bypass normal OpenClaw refresh behavior.

Stopped agents or failed monitor reads raise an agent/monitoring alert. Failed Discord sends stay pending and retry next run. State is written atomically. Discord nonces reduce duplicate sends during short crash/retry windows.

## Operations

Run `python3 -m unittest -v` in this directory. Run a manual check with `python3 monitor.py --config /absolute/path/config.json`. Inspect `config.state.json` for `last_completed`, current incidents, and collection errors. Use system logs tagged `zedbiz-model-alerts` for delivery errors.

To update, copy the tracked Python files into each deployment directory and rerun tests. Preserve protected configuration and state. If Marsha or Harry's Discord bot token rotates, update the respective monitor's protected configuration from the resolved running agent credential without printing it.

To disable, remove only the crontab line marked `# zedbiz-model-alerts`. Keep other cron entries intact. No OpenClaw runtime code was changed.

## Limits

This is not external whole-host uptime monitoring: a powered-off VPS, failed cron service, lost network, or broken Discord credential can prevent notifications. Checks cover configured primary models, not arbitrary session overrides. Catch-up is limited to the last hour. Idle recovery waits for the next real successful primary reply. The normal detection interval is about one minute for logged failures and five minutes for idle credential revocation; unusually slow reads can increase it.

## Verification on September 7, 2026

- Four unit tests passed on both hosts: configured-primary log parsing, duplicate suppression, failed-delivery pending state, and successful-reply recovery ordering.
- Marsha was tested first using simulated failure/recovery events and real, clearly labeled Discord TEST messages. Both messages and Jack's mention were read back through Discord's API. No live outage was induced.
- VPS2 sent a separate TEST notification; its content and mention were read back.
- Full live checks returned VPS1 checked=11, VPS2 checked=3, notices=0.

Test evidence: Discord messages `1546673096411451474`, `1546673097724403822`, and `1546673797615190086` in the destination channel.
