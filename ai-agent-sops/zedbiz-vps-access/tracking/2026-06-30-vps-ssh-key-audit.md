# 2026-06-30 - VPS SSH Key Audit

## Summary

- **Date:** 2026-06-30 Mountain Time
- **Agent:** Cody
- **System:** ZedBiz VPS access keys
- **Change Type:** access-audit, documentation-update
- **Status:** done
- **Priority:** p2-medium

---

## Why This Was Done

The local `Test-Keys` folder had four SSH key information files, but only three VPS lanes were expected: VPS1, VPS2, and VPS3. The goal was to verify which key works for which server, clean up the local notes, and identify whether the fourth key was active or stale.

No private key material was committed to GitHub.

---

## Verified Results

| File | Server | Login | Host/IP | Verified Hostname | Result |
|------|--------|-------|---------|-------------------|--------|
| `z-main-vps.txt` | VPS1 main OpenClaw | `jackadmin` | `187.77.210.223` | `srv1404026` | Active |
| `Cody_key.txt` | VPS1 main OpenClaw | `jackadmin` | `187.77.210.223` | `srv1404026` | Active alternate key |
| `vps2-ssh-key-info.txt` | VPS2 Harry/OpenClaw | `root` | `harry.zbiz.ca` / `2.24.104.80` | `srv1677638` | Active |
| `vps3.txt` | VPS3 Ruby/Hermes | `root` | `2.25.210.154` / `ruby.zbiz.ca` | `srv1764917` | Active |

---

## Fourth Key Finding

`Cody_key.txt` is not a VPS4 key. It is an active alternate key for VPS1 using `jackadmin@187.77.210.223`.

It did not authenticate to VPS2 or VPS3, which is the expected security posture.

---

## Local File Updates

Updated the four local files in `D:\Google Drive\Documents\Codex-Projects\Test-Keys`:

- `z-main-vps.txt` now documents the main VPS1 key.
- `Cody_key.txt` now documents the alternate active VPS1 Cody key.
- `vps2-ssh-key-info.txt` now documents the VPS2 Harry/OpenClaw key.
- `vps3.txt` now documents the VPS3 Ruby/Hermes key.

Each file now includes:

- Tested date in Mountain Time
- Active/inactive status
- Correct server and login user
- Host/IP and verified hostname
- Fingerprint
- Quick-use command
- Secret handling note telling the user to save only the private key block into a key file

---

## Notion Record

Created a Tech Updates journal entry:

- `2026-06-30 | Cody | VPS SSH Key Audit - VPS1, VPS2, VPS3`
- Notion URL: https://app.notion.com/p/38fa3e33d581819da976ef2f4fc78172

---

## Security Note

Private keys remain local only and were not copied into this repository.
