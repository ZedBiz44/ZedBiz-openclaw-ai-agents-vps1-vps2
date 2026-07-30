import fs from "node:fs";
import path from "node:path";

const workspace = process.argv[2] ?? "/home/node/.openclaw/workspace";
const suffix = process.env.AMANDA_REPAIR_BACKUP_SUFFIX ?? "pre-identity-tool-repair";

function update(relativePath, replacements) {
  const filePath = path.join(workspace, relativePath);
  let text = fs.readFileSync(filePath, "utf8");
  const backupPath = `${filePath}.${suffix}`;
  if (!fs.existsSync(backupPath)) {
    fs.copyFileSync(filePath, backupPath);
  }

  for (const [before, after] of replacements) {
    if (!text.includes(before)) {
      throw new Error(`Expected text was not found in ${relativePath}: ${before}`);
    }
    text = text.replace(before, after);
  }

  fs.writeFileSync(filePath, text);
  console.log(`Updated ${relativePath}`);
}

update("AGENTS.md", [
  [
    "- Acknowledge assignments immediately. If tool work is required, say it is underway and provide concise progress updates.",
    "- Start assignments immediately. In Discord or Slack, use non-terminal commentary for progress and reserve the `message` tool for the final user-visible response. In Telegram, follow the Telegram delivery rule below.",
  ],
  [
    "- In Discord or Slack, one natural emoji reaction may replace an unnecessary acknowledgement message.",
    "- In Discord or Slack, one natural emoji reaction may replace an unnecessary acknowledgement. Never call the `message` tool for an intermediate acknowledgement or progress update because OpenClaw treats that result as terminal and can end the work turn.",
  ],
]);

update("TOOLS.md", [
  [
    "Primary Asana route: the agent's PAT-based MCP server, expected as `@roychri/mcp-server-asana` with `ASANA_ACCESS_TOKEN` supplied by the approved runtime secret store.",
    "Primary Asana route: the PAT-backed Streamable HTTP MCP server named `asana`, with `ASANA_ACCESS_TOKEN` supplied by the approved runtime secret store.",
  ],
  [
    "Required tool coverage before task execution: current-user lookup, assigned-task search, task read, task comment, task update/complete, and GID resolution.",
    "Required tool coverage before task execution: `asana_get_user` with `user_gid: \"me\"`, assigned-task search, task read, task comment, task update/complete, and GID resolution.\n\nTreat successful real PAT tool calls and the internal `/healthz` endpoint as authoritative. Do not block solely because `openclaw mcp probe asana` returns HTTP/SSE 400; that legacy probe is incompatible with this Streamable HTTP route.",
  ],
]);
