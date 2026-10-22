# Model monitor compressed-record repair

Verified by Cody, October 9, 2026, Mountain Time. Owner: Victor.

The existing per-minute host monitor reads each configured agent database read-only and reports model/service-monitoring incidents to its existing Discord channel. Keep monitoring failures and recovery notices enabled; Jack explicitly requires these reports.

## Defect and correction

The old reader assumed every transcript_events.event_json held JSON. Current OpenClaw sometimes stores a NULL there and zstd bytes in event_zstd, with event_utf8_bytes describing the decoded size. json.loads(None) crashed the reader. The generic service notice hid this cause, while the advancing global cursor skipped the failed period on the next run and could announce recovery without rereading it.

The corrected reader handles both storage formats. Its libzstd decoder follows the installed OpenClaw transcript-payload bounds and exact decoded-size check (4 MiB maximum compressed payload). It rejects damaged data, invalid JSON, and size mismatches without printing private transcript text. It uses the already installed libzstd; no OpenClaw CLI or model process is launched for decoding.

A per-agent retry_since persists through failed reads, later scheduled runs, and model-incident acknowledgement. It is removed only after the collection and log reads complete. Monitoring notices retain Jack mentions and the same channel, identify the read error, and do not claim that an agent or model failed merely because monitoring failed. Recovery retains the existing quiet period and requires rereading the failed period. The last sanitized error stays in state and is also logged.

## Deployment and verification

Applied under Jack's explicit instruction to get this repair done:
- VPS1: /home/jackadmin/model-alerts/monitor.py, eleven Docker agents.
- VPS2: /opt/zedbiz-model-alerts/monitor.py, Harry, Suzy and Frank.
- Source and state backed up under the existing monitor lock before atomic replacement. All agents were seeded to reread from October 9 09:25 MDT. Pending notices were not cleared.
- Fourteen tests passed on each host: plain and real zstd records, corrupt payloads, size/bounds/JSON failures, persistent retries beyond an hour, proven recovery, unavailable-service alerts, privacy, existing model/fallback behaviour and delivery retry.
- Read-only replay from 09:25 succeeded for all fourteen monitored agents. VPS1 reads took 0.18–0.55 seconds each.
- Two actual scheduled rounds on each host subsequently completed with no collection errors or pending rereads. Journal entries confirm VPS1 checked 11 and VPS2 checked 3, zero new notices in those rounds.
- No agent restart, database write, memory adjustment, channel change or schedule change was required. Ruby and Rocky are outside this particular monitor configuration; this is not a claim of fleet-wide health closure.

Run tests on Linux with libzstd installed: python3 -m unittest -v from this directory.

## Rollback

VPS1 backup: /home/jackadmin/model-alerts/backup-compressed-reader-20261009T161301Z
VPS2 backup: /opt/zedbiz-model-alerts/backup-compressed-reader-20261009T161328Z

Acquire the existing config.lock before replacing monitor.py with the backed-up monitor.py, preserve its mode, and release the lock. No service restart is needed; the next cron run loads the source. Keep current state by default: restoring old state can lose incident evidence and repeat notices. The backup config.state.json is forensic recovery material, not an automatic rollback step. Rolling back code reintroduces the compressed-record defect.

Production SHA256 (both hosts, deployed line endings): d4e390797d4dfd0b7da81d4d931ad547767ae0161416bbbf1b1a0fa0505bc697.
Git normalizes source line endings; compare normalized contents if hashes differ.

## Tracking

Broader incident remains open: https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/6
Technical Journal: https://www.notion.so/3f3a3e33d581814a992cf02511f05798
This repair resolves the reproduced model-monitor reader defect; earlier memory, performance, access and security findings retain their own evidence and dispositions.
