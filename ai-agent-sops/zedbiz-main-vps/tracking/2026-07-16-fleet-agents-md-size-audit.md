# VPS1 and VPS2 AGENTS.md Size Audit

Date: 2026-07-16 Mountain Time  
Verified by: Cody  
Status: Read-only audit complete

## Purpose

Measure the live `AGENTS.md` character count for every active OpenClaw agent on VPS1 and VPS2 and verify the OpenClaw bootstrap-size Doctor check.

## Results

| Agent | VPS | Characters | Headroom Below 20,000 | Doctor |
| --- | --- | ---: | ---: | --- |
| Amanda | VPS1 | 19,915 | 85 | Pass |
| Terry | VPS1 | 19,822 | 178 | Pass |
| Edith | VPS1 | 19,411 | 589 | Pass |
| Wilma | VPS1 | 18,882 | 1,118 | Pass |
| Harry | VPS2 | 17,763 | 2,237 | Pass |
| Gohzed | VPS1 | 17,708 | 2,292 | Pass |
| Vivian | VPS1 | 17,518 | 2,482 | Pass |
| Grogar | VPS1 | 17,514 | 2,486 | Pass |
| Inga | VPS1 | 17,513 | 2,487 | Pass |
| Maggie | VPS1 | 17,481 | 2,519 | Pass |
| Victor | VPS1 | 17,339 | 2,661 | Pass |
| Suzy | VPS2 | 16,738 | 3,262 | Pass |
| Frank | VPS2 | 12,621 | 7,379 | Pass |
| Marsha | VPS1 | 11,360 | 8,640 | Pass |

## Assessment

- Amanda and Terry are effectively at the ceiling and should be shortened first.
- Edith and Wilma should be shortened before more fleet rules are added.
- Harry, Gohzed, Vivian, Grogar, Inga, Maggie, and Victor pass but have limited growth room.
- Suzy is acceptable but still above the preferred long-term operating target.
- Frank and Marsha have comfortable headroom.

## Verification

- Measured live UTF-8 character counts rather than relying only on file byte size.
- Ran the read-only `core/doctor/bootstrap-size` check for every agent.
- All fourteen agents returned zero bootstrap-size findings.
- No live files were changed.

## Recommendation

Use the proven Marsha cleanup pattern. Target approximately 12,000 to 15,000 characters per agent, preserve agent-specific authority and routing rules, and move technical inventory or detailed procedures to the appropriate tool file, heartbeat file, or skill.
