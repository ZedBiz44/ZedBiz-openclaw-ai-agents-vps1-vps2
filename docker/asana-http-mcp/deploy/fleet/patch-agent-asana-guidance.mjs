import fs from "node:fs";
import path from "node:path";

const [workspace, agentName, email, userGid, backupSuffix] =
  process.argv.slice(2);

if (!workspace || !agentName || !email || !userGid || !backupSuffix) {
  throw new Error(
    "Usage: patch-agent-asana-guidance.mjs <workspace> <name> <email> <gid> <backup-suffix>",
  );
}

const toolsPath = path.join(workspace, "TOOLS.md");
const backupPath = `${toolsPath}.${backupSuffix}`;
if (!fs.existsSync(backupPath)) {
  fs.copyFileSync(toolsPath, backupPath);
}

let text = fs.readFileSync(toolsPath, "utf8");
const heading = "## Asana Identity And Safe Navigation";
const section = `${heading}

- Primary route: the persistent PAT-backed Streamable HTTP MCP server named \`asana\`. Never use Jack's Codex/ChatGPT Asana connector for agent-owned work.
- Required identity: \`${agentName}\`, \`${email}\`, user GID \`${userGid}\`.
- Required workspace: \`ZedBiz - Local Marketing Service\`, GID \`11298561585567\`.
- Begin Asana work with \`asana_get_user\` using \`user_gid: "me"\`; stop if the identity or workspace does not match.
- Resolve names across projects, teams, and accessible portfolios instead of guessing the object type.
- For a team, use \`asana_search_teams\`, then \`asana_get_projects_for_team\` with the resolved team GID.
- For read-only portfolio work, use \`asana_list_accessible_portfolios\`, \`asana_get_portfolio\`, and \`asana_get_portfolio_items\`.
- Portfolio access is Viewer-only unless Jack explicitly approves a broader role. Do not change portfolio membership, sharing, roles, or structure.
- Treat a successful real PAT tool call and the sidecar \`/healthz\` endpoint as authoritative. A legacy \`openclaw mcp probe asana\` HTTP/SSE 400 does not by itself prove this Streamable HTTP route is broken.
`;

const start = text.indexOf(heading);
if (start === -1) {
  text = `${text.trimEnd()}\n\n${section}`;
} else {
  const nextHeading = text.indexOf("\n## ", start + heading.length);
  text =
    nextHeading === -1
      ? `${text.slice(0, start)}${section}`
      : `${text.slice(0, start)}${section}\n${text.slice(nextHeading + 1)}`;
}

text = text.replace(
  /Primary Asana route:[^\n]*@roychri\/mcp-server-asana[^\n]*/g,
  "Primary Asana route: the persistent PAT-backed Streamable HTTP MCP server named `asana`.",
);

fs.writeFileSync(toolsPath, `${text.trimEnd()}\n`);
console.log(`Updated ${toolsPath}`);
