# 2026-07-20 - Z-Code Bootstrap Import

## Summary

- **Date:** 2026-07-20 Mountain Time
- **Agent:** Cody
- **Source:** Live Notion `Content-Master-Databases` page and every linked Core Content Database
- **Result:** Existing codes imported and verified; new allocation remains locked pending conflict resolution

## Source Inventory

- Queried all nineteen linked database surfaces, including both linked Tools databases, Clients, Prospects, and archived-row views.
- Rows inspected: 549
- Rows with a Z-Code: 349
- Blank Z-Code rows: 200
- Validly formatted Z-Code rows: 349
- Distinct Z-Codes: 336
- Distinct topic groups: 78
- Archived rows found: 0
- Invalid Z-Code formats found: 0

## Bootstrap Result

- Imported one record first and verified its API lookup before continuing.
- Imported 336 distinct Z-Codes as active historical allocations.
- Imported 78 topic groups.
- SQLite `PRAGMA quick_check`: `ok`
- Duplicate codes in SQLite: 0
- Duplicate topic/suffix pairs in SQLite: 0
- Allocation remained disabled during and after import.
- Post-import backup: `/opt/zedbiz-services/z-code-allocator/data/backups/zcode-bootstrap-20260720T202705Z.db`
- Backup SHA-256: `51e4e6a18bf68c3cb1a944dc068a4f7a215196f45857a4757f0f07b1a3dfe2fb`

## Name-Key Mapping

- Derived the stable Name-Key from the canonical Brief title for seventy topic groups.
- Derived the remaining eight from their Biz-Plan, Research, or Website title.
- Disambiguated the existing Three-Ps records as `Three-Ps-Product`, `Three-Ps-Service`, and `Three-Ps-Prospect` because the allocator requires a globally unique Name-Key.
- Used `Paradise-Lifestyle-Club` as the temporary canonical Name-Key for topic `ZVIM-20001-100009` because most records in that topic group belong to Paradise Lifestyle Club.

## Notion Conflicts Found

### LightningIM Code Copied Into Example Rows

- Code: `ZVIM-20003-100003-020`
- Twelve Notion rows contain this code.
- The canonical imported record is `LightningIM-Biz-Plan-90-Day-Improvement-Plan`.
- Eleven `AA-Example` rows across unrelated databases also contain it and should have their Z-Code cleared or corrected.

### Deals7 And Paradise Lifestyle Club Share One Brief Code

- Code: `ZVIM-20001-100009-010`
- Both `Deals7-Brief-Affiliate-Deals-And-Link-Forwarding` and `Paradise-Lifestyle-Club-Brief-Venture-Overview` contain this code.
- The topic group also contains a Deals7 source record at suffix `059` among the Paradise Lifestyle Club records.
- Paradise Lifestyle Club was used as the temporary canonical topic so the code remains occupied, but Deals7 requires a separate topic assignment.

### Rocky Mountain Music Culture Duplicate Suffix

- Code: `ZVIM-20001-100011-052`
- Both `Rocky-Mountain-Music-Culture-Jack-Free-Spirit-Vixens-Concept` and `Rocky-Mountain-Music-Culture-Research-Rocky-Mountiain-Music-Alberta-Music-Festivals-And-Events-Historical` contain this code.
- The Research record was used as the canonical imported URL so the suffix remains occupied.
- One of the two Notion records requires a new suffix.

## Safety Decision

- Each conflicting code was imported once so the allocator cannot issue it again.
- No Notion record was changed during extraction or bootstrap.
- New allocation remains locked until Jack approves the three Notion corrections.

