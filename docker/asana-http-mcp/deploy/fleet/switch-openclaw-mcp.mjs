import fs from "node:fs";

const [configPath, agent] = process.argv.slice(2);
if (!configPath || !agent) {
  throw new Error("Usage: switch-openclaw-mcp.mjs <openclaw.json> <agent>");
}

const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
config.mcp ??= {};
config.mcp.servers ??= {};

config.mcp.servers.asana = {
  url: `http://${agent}-asana-mcp:8080/mcp`,
  headers: {
    Authorization: "Bearer ${ASANA_ACCESS_TOKEN}",
  },
};

fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`, {
  mode: 0o600,
});

console.log(`Switched ${agent}'s standard Asana route to persistent HTTP`);
