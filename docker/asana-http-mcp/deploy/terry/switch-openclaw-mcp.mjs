import fs from "node:fs";

const configPath = process.argv[2] ?? "/home/node/.openclaw/openclaw.json";
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));

if (!config.mcp?.servers?.asana) {
  throw new Error("Expected existing asana MCP definition");
}

config.mcp.servers.asana = {
  url: "http://terry-asana-mcp:8080/mcp",
  headers: {
    Authorization: "Bearer ${ASANA_ACCESS_TOKEN}",
  },
};

fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`, {
  mode: 0o600,
});

console.log("Switched Terry's asana route to the persistent HTTP MCP endpoint");
