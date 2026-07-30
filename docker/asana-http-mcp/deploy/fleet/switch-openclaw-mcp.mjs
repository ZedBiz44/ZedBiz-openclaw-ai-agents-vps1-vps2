import fs from "node:fs";

const [configPath, agent, toolset = "standard"] = process.argv.slice(2);
if (!configPath || !agent) {
  throw new Error(
    "Usage: switch-openclaw-mcp.mjs <openclaw.json> <agent> [standard|advanced]",
  );
}
if (!["standard", "advanced"].includes(toolset)) {
  throw new Error("toolset must be standard or advanced");
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
if (toolset === "advanced") delete config.mcp.servers["asana-team"];

fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`, {
  mode: 0o600,
});

console.log(`Switched ${agent}'s ${toolset} Asana route to persistent HTTP`);
