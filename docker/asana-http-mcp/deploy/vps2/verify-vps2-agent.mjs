import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const [agent, url, expectedEmail, workspaceGid = "11298561585567"] = process.argv.slice(2);
const token = process.env.MCP_AUTH_TOKEN;

if (!agent || !url || !expectedEmail || !token) {
  throw new Error(
    "Usage: MCP_AUTH_TOKEN=<resolved-token> node verify-vps2-agent.mjs <agent> <url> <expected-email> [workspace-gid]",
  );
}

const requiredTools = [
  "asana_get_user",
  "asana_get_my_tasks",
  "asana_get_task",
  "asana_create_task_story",
  "asana_update_task",
];

const client = new Client({ name: "zedbiz-vps2-asana-verify", version: "1.0.0" });
const transport = new StreamableHTTPClientTransport(new URL(url), {
  requestInit: { headers: { Authorization: `Bearer ${token}` } },
});

async function call(name, args) {
  const result = await client.callTool({ name, arguments: args });
  if (result.isError) throw new Error(`${name} returned an MCP error`);
  const text = result.content?.[0]?.text;
  if (!text) throw new Error(`${name} returned no textual result`);
  return JSON.parse(text);
}

try {
  await client.connect(transport);
  const toolList = await client.listTools();
  const toolNames = new Set(toolList.tools.map((tool) => tool.name));
  const missingTools = requiredTools.filter((name) => !toolNames.has(name));
  if (missingTools.length) {
    throw new Error(`Required tools missing: ${missingTools.join(", ")}`);
  }

  const me = await call("asana_get_user", {
    user_gid: "me",
    workspace_gid: workspaceGid,
  });
  if (me.email !== expectedEmail) {
    throw new Error(`Identity email mismatch for ${agent}`);
  }
  if (!me.workspaces?.some((workspace) => workspace.gid === workspaceGid)) {
    throw new Error(`Required workspace is unavailable for ${agent}`);
  }

  const myTasks = await call("asana_get_my_tasks", {
    workspace: workspaceGid,
    completed_since: "now",
    opt_fields: "gid",
  });

  const taskCount = Array.isArray(myTasks) ? myTasks.length : 0;
  console.log(
    JSON.stringify({
      ok: true,
      agent,
      tool_count: toolList.tools.length,
      identity: { email: me.email, gid: me.gid },
      workspace_gid: workspaceGid,
      assigned_incomplete_task_count: taskCount,
    }),
  );
} finally {
  await client.close();
}
