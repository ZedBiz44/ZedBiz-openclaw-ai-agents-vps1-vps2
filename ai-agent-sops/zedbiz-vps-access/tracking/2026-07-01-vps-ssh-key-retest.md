# 2026-07-01 - VPS SSH Key Retest

## Summary

- **Date:** 2026-07-01 Mountain Time
- **Agent:** Cody
- **System:** ZedBiz VPS access keys
- **Change Type:** access-audit, verification
- **Status:** done
- **Priority:** p2-medium

---

## Why This Was Done

The SSH key files were renamed and centralized under:

```text
D:\Google Drive\Documents\Codex-Projects\.ssh
```

The goal was to retest the renamed keys and confirm that they still authenticate to the correct VPS targets.

No private key material was committed to GitHub.

---

## Verified Results

| File | Server | Login | Host/IP | Verified Hostname | Result |
|------|--------|-------|---------|-------------------|--------|
| `vps1-ssh-key.txt` | VPS1 main OpenClaw | `jackadmin` | `187.77.210.223` | `srv1404026` | Active |
| `vps1-ssh-key-bu.txt` | VPS1 main OpenClaw | `jackadmin` | `187.77.210.223` | `srv1404026` | Active alternate key |
| `vps2-ssh-key.txt` | VPS2 Harry/OpenClaw | `root` | `harry.zbiz.ca` / `2.24.104.80` | `srv1677638` | Active |
| `vps3.ssh-key.txt` | VPS3 Ruby/Hermes | `root` | `2.25.210.154` / `ruby.zbiz.ca` | `srv1764917` | Active |

---

## Security Checks

- VPS1 root login remains denied, which matches the intended `jackadmin` lane.
- VPS1 keys were denied by VPS2 and VPS3.
- VPS2 key was denied by VPS1 and VPS3.
- VPS3 key was denied by VPS1 and VPS2.

This confirms the keys are not broadly interchangeable across servers.

---

## Backup Folder Observation

The backup folder also contains the four renamed key-note files:

```text
C:\Users\zener\.ssh
```

It also contains extra VPS3 temp/normalized files from earlier work. Two match the active VPS3 key fingerprint, and one appears malformed/not useful as a private key. Cleanup can be handled separately so only the four intended backup files remain.

---

## Notion Record

Created Tech Updates journal entry:

- `2026-07-01 | Cody | VPS SSH Key Retest`
- Notion URL: https://app.notion.com/p/390a3e33d581810cbcb4e5fe281d79c4
