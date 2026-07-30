import fs from "node:fs";
import path from "node:path";

const [workspace, toolset, agentName, email, userGid, backupSuffix] =
  process.argv.slice(2);

if (
  !workspace ||
  !["standard", "advanced"].includes(toolset) ||
  !agentName ||
  !email ||
  !userGid ||
  !backupSuffix
) {
  throw new Error(
    "Usage: patch-agent-asana-guidance-v2.mjs <workspace> <standard|advanced> <name> <email> <gid> <backup-suffix>",
  );
}

const toolsPath = path.join(workspace, "TOOLS.md");
const backupPath = `${toolsPath}.${backupSuffix}`;
if (!fs.existsSync(backupPath)) fs.copyFileSync(toolsPath, backupPath);

let body = fs.readFileSync(toolsPath, "utf8");
const heading = "## Asana Identity And Toolset";
const oldHeading = "## Asana Identity And Safe Navigation";
const advancedLines =
  toolset === "advanced"
    ? `
- This agent has the 126-tool Asana Advanced toolset, which includes every Standard tool plus team, portfolio, custom-field, goal, template, webhook, workload, and organization-level operations.
- Automatically load \`zedbiz-advanced-asana-control\` for team administration, portfolio mutations, workspace custom-field administration, goals administration, webhooks, broad structural changes, or an operation requiring \`asana_api_request\`.
- There is no separate \`asana-team\` route. All Standard and Advanced tools come from the single \`asana\` route.
- Prefer a named tool. Use \`asana_api_request\` only for a supported public Asana API endpoint with no named tool, and never to bypass approval rules.
`
    : `
- This agent has the 76-tool Asana Standard toolset for normal team, project, task, subtask, section, project-status, project-brief, tag, attachment, date, dependency, blocker, and read-only portfolio work.
- Team administration, portfolio mutations, workspace custom-field administration, goals administration, webhooks, and unrestricted API operations require an approved Advanced agent.
`;

const section = `${heading}

- Primary route: the persistent PAT-backed Streamable HTTP MCP server named \`asana\`. Never use Jack's Codex/ChatGPT Asana connector for agent-owned work.
- Toolset: \`${toolset}\`.
- Required identity: \`${agentName}\`, \`${email}\`, user GID \`${userGid}\`.
- Required workspace: \`ZedBiz - Local Marketing Service\`, GID \`11298561585567\`.
- Begin Asana work with \`asana_get_user\` using \`user_gid: "me"\`; stop if identity or workspace does not match.
- Resolve names across projects, teams, and portfolios instead of guessing the object type.
- Treat a successful real PAT tool call and the sidecar \`/healthz\` endpoint as authoritative. A legacy \`openclaw mcp probe asana\` HTTP/SSE 400 does not by itself prove the Streamable HTTP route is broken.
${advancedLines}`;

let start = body.indexOf(heading);
if (start === -1) start = body.indexOf(oldHeading);
if (start === -1) {
  body = `${body.trimEnd()}\n\n${section}`;
} else {
  const nextHeading = body.indexOf("\n## ", start + 3);
  body =
    nextHeading === -1
      ? `${body.slice(0, start)}${section}`
      : `${body.slice(0, start)}${section}\n${body.slice(nextHeading + 1)}`;
}

fs.writeFileSync(toolsPath, `${body.trimEnd()}\n`);
console.log(`Updated ${toolsPath} for ${toolset}`);
