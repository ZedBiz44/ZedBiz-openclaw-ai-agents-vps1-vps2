# 2026-07-11 | Cody | Asana Skill Split and Enhancements

Date: 2026-07-11 | Agent: Cody | Status: Complete

## Summary

Updated the regular Asana Agent Control Skill and built out the Advanced Asana Skill page for Amanda, Marsha, and Ruby.

## Work Completed

- Clarified that custom endpoint support does not belong in the regular skill right now because the current OpenClaw SOP uses `@roychri/mcp-server-asana` with `ASANA_ACCESS_TOKEN` and no documented custom endpoint variable.
- Clarified that `notion-rest` is not an Asana authentication fallback and must not be used to bypass failed PAT MCP authentication.
- Added daily-agent skill boundaries, safe action levels, tool path audit, task claiming, completion rules, blocker handling, GID resolution, custom field enumeration, rich text mention guidance, attachments, and scheduled Events guidance.
- Moved advanced Asana administration items into the Advanced Asana Skill page.
- Built the Advanced Asana Skill page with overview, design, contents, actual skill copy, implementation SOP, user guide, and future enhancements.

## Related Notion Records

- Regular Asana Agent Control Skill: https://app.notion.com/p/399a3e33d5818001ad46f29b4f204b22
- Advanced Asana Skill: https://app.notion.com/p/39aa3e33d5818005808cd9f3c6785136
- Tech Updates journal: https://app.notion.com/p/39aa3e33d581816bb347d04710410616

## Decision

Regular agents use the base Asana Agent Control Skill for assigned task execution only. Advanced Asana administration belongs with Amanda, Marsha, Ruby, or another Jack-approved top-level Asana agent.
