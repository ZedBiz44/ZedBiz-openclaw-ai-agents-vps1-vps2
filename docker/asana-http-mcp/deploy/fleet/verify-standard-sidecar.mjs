import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const [
  expectedUserGid,
  expectedEmail,
  expectedPortfolioCount = "5",
  expectedTeamGid = "1216007690588299",
  expectedTeamName = "Z1AM-ZedBiz-Main",
] = process.argv.slice(2);

if (!expectedUserGid || !expectedEmail) {
  throw new Error(
    "Usage: verify-standard-sidecar.mjs <user-gid> <email> [portfolio-count] [team-gid] [team-name]",
  );
}

const workspaceGid = "11298561585567";
const token = process.env.MCP_AUTH_TOKEN;
if (!token) throw new Error("MCP_AUTH_TOKEN is missing");

const client = new Client({ name: "zedbiz-fleet-verify", version: "1.0.0" });
const transport = new StreamableHTTPClientTransport(
  new URL("http://127.0.0.1:8080/mcp"),
  {
    requestInit: {
      headers: { Authorization: `Bearer ${token}` },
    },
  },
);

const call = async (name, args) => {
  const result = await client.callTool({ name, arguments: args });
  if (result.isError) throw new Error(`${name} returned an MCP error`);
  return JSON.parse(result.content[0].text);
};

try {
  await client.connect(transport);
  const tools = await client.listTools();
  if (tools.tools.length !== 47) {
    throw new Error(`Expected 47 tools, received ${tools.tools.length}`);
  }

  const me = await call("asana_get_user", {
    user_gid: "me",
    workspace_gid: workspaceGid,
  });
  if (
    me.gid !== expectedUserGid ||
    me.email !== expectedEmail ||
    !me.workspaces.some((workspace) => workspace.gid === workspaceGid)
  ) {
    throw new Error(`Identity mismatch: ${JSON.stringify(me)}`);
  }

  const teams = await call("asana_search_teams", {
    workspace_gid: workspaceGid,
    search_term: expectedTeamName,
  });
  const team = teams.find(
    (candidate) =>
      candidate.gid === expectedTeamGid &&
      candidate.name === expectedTeamName,
  );
  if (!team) throw new Error("Exact team was not resolved");

  const projects = await call("asana_get_projects_for_team", {
    team_gid: expectedTeamGid,
    archived: false,
  });
  const portfolios = await call("asana_list_accessible_portfolios", {
    workspace_gid: workspaceGid,
  });
  const requiredPortfolioCount = Number.parseInt(expectedPortfolioCount, 10);
  if (
    Number.isFinite(requiredPortfolioCount) &&
    portfolios.length !== requiredPortfolioCount
  ) {
    throw new Error(
      `Expected ${requiredPortfolioCount} portfolios, received ${portfolios.length}`,
    );
  }

  console.log(
    JSON.stringify({
      ok: true,
      toolCount: tools.tools.length,
      identity: { gid: me.gid, email: me.email },
      team: { gid: team.gid, name: team.name },
      projectCount: projects.length,
      portfolioCount: portfolios.length,
      portfolios: portfolios.map((portfolio) => ({
        gid: portfolio.gid,
        name: portfolio.name,
        access_level: portfolio.access_level ?? null,
      })),
    }),
  );
} finally {
  await client.close();
}
