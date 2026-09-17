# OpenClaw AGENTS.md Fleet Assessment

Date: 2026-09-17 | Operator: Cody | Status: Deployment candidate

## Scope

- VPS1: Amanda, Edith, GoHZed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- VPS2: Frank, Harry, and Suzy.
- VPS4: Rocky.
- Live files, runtime health, ownership, permissions, version, configured bootstrap limits, supporting bootstrap files, and current GitHub records were inspected before editing.

## Finding

The June cleanup had not simply failed. Later updates repeatedly appended fleet-wide memory, communication, Notion, Asana, email-trigger, and tool notes to otherwise sound role files. That preserved new instructions but recreated duplication and pushed several files close to or beyond the default OpenClaw per-file budget.

## Candidate Sizes

| Agent | VPS | Live characters | Candidate characters | Result |
|---|---:|---:|---:|---|
| Amanda | 1 | 19,272 | 16,314 | Review warning, below live limit |
| Edith | 1 | 25,695 | 17,557 | Restored below live limit |
| GoHZed | 1 | 22,581 | 15,617 | Restored below live limit |
| Grogar | 1 | 22,156 | 14,773 | Restored below live limit |
| Inga | 1 | 22,090 | 13,660 | Within target |
| Maggie | 1 | 22,422 | 16,568 | Restored below live limit |
| Marsha | 1 | 21,179 | 18,510 | Restored below live limit; role breadth exception |
| Terry | 1 | 18,940 | 16,825 | Review warning, below live limit |
| Victor | 1 | 18,109 | 13,263 | Within target |
| Vivian | 1 | 21,510 | 17,142 | Restored below live limit; media exception |
| Wilma | 1 | 19,248 | 16,340 | Review warning, below live limit |
| Frank | 2 | 20,399 | 17,468 | Below configured 24,000 limit |
| Harry | 2 | 18,906 | 14,605 | Below configured 24,000 limit |
| Suzy | 2 | 18,214 | 12,871 | Within target |
| Rocky | 4 | 42,448 | 14,000 | Within target |

## Design Decision

- Preserve role, ownership, approval, security, source-of-truth, tool, memory privacy, email-trigger, and role-specific failure instructions.
- Merge repeated fleet policy into short testable rules.
- Keep environment-specific paths, commands, IDs, and connector inventories in `TOOLS.md`, with a routing rule in `AGENTS.md`.
- Keep detailed procedures in Skills and authoritative technical records in GitHub.
- Do not remove relocated material until its destination exists, routing remains, and fresh-session discovery is proven.
- Files above 14,000 characters are documented exceptions and require fresh-session tail tests.

## Deployment Gate

- Create an external timestamped backup before every live write.
- Re-check the live hash immediately before replacement.
- Preserve owner and mode.
- Pilot one agent first, then verify startup, role behavior, approval boundaries, source routing, local-note discovery, and the final email-trigger section in a fresh session.
- Expand only after the pilot passes. Roll back any agent whose fresh-session behavior or runtime health fails.

