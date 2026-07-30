import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const [
  toolset,
  expectedUserGid,
  expectedEmail,
  expectedTeamGid = "1216007690588299",
  expectedTeamName = "Z1AM-ZedBiz-Main",
] = process.argv.slice(2);

if (!["standard", "advanced"].includes(toolset)) {
  throw new Error("toolset must be standard or advanced");
}
if (!expectedUserGid || !expectedEmail) {
  throw new Error(
    "Usage: verify-toolset.mjs <toolset> <user-gid> <email> [team-gid] [team-name]",
  );
}

const workspaceGid = "11298561585567";
const expectedCount = toolset === "advanced" ? 126 : 76;
const token = process.env.MCP_AUTH_TOKEN;
if (!token) throw new Error("MCP_AUTH_TOKEN is missing");

const client = new Client({ name: "zedbiz-toolset-verify", version: "2.0.0" });
const transport = new StreamableHTTPClientTransport(
  new URL("http://127.0.0.1:8080/mcp"),
  {
    requestInit: {
      headers: { Authorization: `Bearer ${token}` },
    },
  },
);

const call = async (name, args) => {
  const response = await client.callTool({ name, arguments: args });
  if (response.isError) throw new Error(`${name} returned an MCP error`);
  const value = JSON.parse(response.content[0].text);
  if (value?.error) throw new Error(`${name}: ${value.error}`);
  return value;
};

try {
  await client.connect(transport);
  const listed = await client.listTools();
  const names = listed.tools.map((tool) => tool.name);
  if (names.length !== expectedCount) {
    throw new Error(`Expected ${expectedCount} tools, received ${names.length}`);
  }

  const required = [
    "asana_get_user",
    "asana_create_task",
    "asana_create_project_brief",
    "asana_upload_attachment",
    "asana_get_task_dependencies",
    "asana_remove_task_dependencies",
    "asana_get_portfolio_items",
  ];
  if (toolset === "advanced") {
    required.push(
      "asana_create_team",
      "asana_create_portfolio",
      "asana_create_custom_field",
      "asana_api_request",
    );
  }
  const missing = required.filter((name) => !names.includes(name));
  if (missing.length) throw new Error(`Missing tools: ${missing.join(", ")}`);

  const me = await call("asana_get_user", { user_gid: "me" });
  if (
    me.gid !== expectedUserGid ||
    me.email !== expectedEmail ||
    !me.workspaces.some((workspace) => workspace.gid === workspaceGid)
  ) {
    throw new Error(`Identity mismatch: ${JSON.stringify(me)}`);
  }

  const teams = await call("asana_search_teams", {
    workspace_gid: workspaceGid,
    name_pattern: expectedTeamName,
  });
  const team = teams.find(
    (candidate) =>
      candidate.gid === expectedTeamGid &&
      candidate.name === expectedTeamName,
  );
  if (!team) throw new Error("Exact verification team was not resolved");
  const projects = await call("asana_get_projects_for_team", {
    team_gid: expectedTeamGid,
    archived: false,
  });
  const portfolios = await call("asana_list_accessible_portfolios", {
    workspace_gid: workspaceGid,
  });

  let rawIdentity = null;
  if (toolset === "advanced") {
    rawIdentity = await call("asana_api_request", {
      method: "GET",
      path: "/users/me",
      query: { opt_fields: "gid,name,email" },
    });
    if (
      rawIdentity.gid !== expectedUserGid ||
      rawIdentity.email !== expectedEmail
    ) {
      throw new Error(`Advanced API identity mismatch: ${JSON.stringify(rawIdentity)}`);
    }
  }

  console.log(
    JSON.stringify({
      ok: true,
      toolset,
      toolCount: names.length,
      identity: { gid: me.gid, email: me.email },
      team: { gid: team.gid, name: team.name },
      projectCount: projects.length,
      portfolioCount: portfolios.length,
      advancedApiIdentity: rawIdentity
        ? { gid: rawIdentity.gid, email: rawIdentity.email }
        : null,
    }),
  );
} finally {
  await client.close();
}
