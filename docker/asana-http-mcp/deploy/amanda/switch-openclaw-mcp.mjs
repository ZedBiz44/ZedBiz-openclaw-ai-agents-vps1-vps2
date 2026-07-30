import fs from "node:fs";

const configPath = process.argv[2] ?? "/home/node/.openclaw/openclaw.json";
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));

if (!config.mcp?.servers?.asana || !config.mcp?.servers?.["asana-team"]) {
  throw new Error("Expected existing asana and asana-team MCP definitions");
}

config.mcp.servers.asana = {
  url: "http://amanda-asana-mcp:8080/mcp",
  headers: {
    Authorization: "Bearer ${ASANA_ACCESS_TOKEN}",
  },
};

config.mcp.servers["asana-team"] = {
  url: "http://amanda-asana-team-mcp:8080/mcp",
  headers: {
    Authorization: "Bearer ${ASANA_ACCESS_TOKEN}",
  },
};

fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`, {
  mode: 0o600,
});

console.log("Switched asana and asana-team to persistent HTTP MCP endpoints");
