import fs from "node:fs";
import path from "node:path";

const workspace = process.argv[2] ?? "/home/node/.openclaw/workspace";
const suffix = process.env.TERRY_REPAIR_BACKUP_SUFFIX ?? "pre-read-navigation-repair";

function readAndBackup(relativePath) {
  const filePath = path.join(workspace, relativePath);
  const backupPath = `${filePath}.${suffix}`;
  if (!fs.existsSync(backupPath)) {
    fs.copyFileSync(filePath, backupPath);
  }
  return { filePath, text: fs.readFileSync(filePath, "utf8") };
}

function write(relativePath, transform) {
  const { filePath, text } = readAndBackup(relativePath);
  const updated = transform(text);
  if (updated === text) {
    console.log(`No change needed in ${relativePath}`);
    return;
  }
  fs.writeFileSync(filePath, updated);
  console.log(`Updated ${relativePath}`);
}

write("AGENTS.md", (text) => {
  const oldText =
    "- Acknowledge assignments immediately. If tools or analysis are required, say work is underway.";
  const newText =
    "- Start assignments immediately. In Discord or Slack, use non-terminal commentary for progress and reserve the `message` tool for the final user-visible response. Never call the `message` tool for an intermediate acknowledgement because OpenClaw may treat it as terminal and interrupt the work turn.";

  if (text.includes(newText)) return text;
  if (!text.includes(oldText)) {
    throw new Error("Expected Terry acknowledgement rule was not found in AGENTS.md");
  }
  return text.replace(oldText, newText);
});

write("TOOLS.md", (text) => {
  const oldRoute =
    "Primary Asana route: the agent's PAT-based MCP server, expected as `@roychri/mcp-server-asana` with `ASANA_ACCESS_TOKEN` supplied by the approved runtime secret store.";
  const newRoute =
    "Primary Asana route: the persistent PAT-backed Streamable HTTP MCP server named `asana`, with `ASANA_ACCESS_TOKEN` supplied by the approved runtime secret store.";

  if (text.includes(oldRoute)) {
    text = text.replace(oldRoute, newRoute);
  } else if (!text.includes(newRoute)) {
    throw new Error("Expected Terry primary Asana route was not found in TOOLS.md");
  }

  const marker = "## Asana Identity And Read Navigation";
  if (!text.includes(marker)) {
    text += `

${marker}

- Begin Asana work with \`asana_get_user\` using \`user_gid: "me"\`; verify Terry's PAT identity and workspace before trusting results.
- Treat a successful real PAT tool call and the service \`/healthz\` endpoint as authoritative. A legacy \`openclaw mcp probe asana\` HTTP/SSE 400 does not prove this Streamable HTTP route is broken.
- Never infer that a name is a portfolio merely because project search returned no result.
- Resolve ambiguous names across projects, teams, and accessible portfolios.
- For a team, use \`asana_search_teams\`, then \`asana_get_projects_for_team\` with the resolved team GID.
- For read-only portfolio work, use \`asana_list_accessible_portfolios\`, \`asana_get_portfolio\`, and \`asana_get_portfolio_items\`.
- An empty portfolio list means Terry currently has no visible portfolio ownership or membership. It does not prove the workspace has no portfolios.
- Do not change team membership, portfolio sharing, portfolio roles, or portfolio structure without the advanced Asana policy and Jack's confirmation.
`;
  }

  return text;
});
