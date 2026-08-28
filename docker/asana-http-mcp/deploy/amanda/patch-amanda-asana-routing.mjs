import fs from "node:fs";
import path from "node:path";

const workspace = process.argv[2] ?? "/home/node/.openclaw/workspace";
const suffix = process.env.ROUTING_BACKUP_SUFFIX ?? "pre-http-mcp-routing";

function update(relativePath, replacements) {
  const filePath = path.join(workspace, relativePath);
  let text = fs.readFileSync(filePath, "utf8");
  const backupPath = `${filePath}.${suffix}`;
  if (!fs.existsSync(backupPath)) {
    fs.copyFileSync(filePath, backupPath);
  }

  for (const [before, after] of replacements) {
    if (!text.includes(before)) {
      throw new Error(`Expected routing text was not found in ${relativePath}`);
    }
    text = text.replace(before, after);
  }

  fs.writeFileSync(filePath, text);
  console.log(`Updated ${relativePath}`);
}

update("AGENTS.md", [
  [
    "- Use the day-to-day Asana agent-control skill for assigned task work and the advanced Asana-control skill only for approved project-level operations.",
    "- Use the day-to-day Asana agent-control skill for assigned task work. Automatically load the advanced Asana-control skill for team or membership management and approved project-level operations. Use `asana-team` only for its six team/membership tools; use `asana` for task, project, section, status, dependency, and other supported project operations.",
  ],
]);

update("TOOLS.md", [
  [
    "Amanda may use advanced Asana operations only through the PAT-authenticated Asana MCP after identity preflight.\n\nAdvanced work includes project briefs, status updates, custom fields, sections, task ordering, dependencies, blockers, bulk date shifts, portfolios, and reporting-impacting changes.",
    "Amanda must automatically load the advanced Asana-control skill when a request involves team creation, team updates, team membership, project administration, project briefs, status updates, custom fields, sections, task ordering, dependencies, blockers, bulk date shifts, portfolios, workflow changes, or reporting-impacting changes.\n\nTool routing is separate from skill routing:\n\n- Use `asana-team` for its six team and membership operations: list teams, update a team, create a team, add a team member, remove a team member, and list team members.\n- Use `asana` for normal task work and for advanced project operations supported by its project, section, status, dependency, and task tools.\n- Never substitute a Jack-authenticated Codex/ChatGPT Asana connector for either route.\n\nBoth routes require Amanda's PAT identity preflight.",
  ],
]);

update("skills/z-advanced-asana-control/SKILL.md", [
  [
    "description: Use only for approved top-level ZedBiz Asana agents such as Amanda, Marsha, and Ruby when managing Asana projects, status updates, project briefs, custom fields, sections, task ordering, dependencies, blockers, bulk date shifts, and higher-level Asana workflow improvements.",
    "description: Use only for approved top-level ZedBiz Asana agents such as Amanda, Marsha, and Ruby when managing Asana teams or memberships, projects, status updates, project briefs, custom fields, sections, task ordering, dependencies, blockers, bulk date shifts, and higher-level Asana workflow improvements.",
  ],
  [
    "## Advanced Work Boundary\n",
    "## Automatic Skill And Tool Routing\n\nLoad this skill automatically when the request involves Asana team creation, team updates, team membership, project administration, project briefs, project status, custom fields, sections, ordering, dependencies, blockers, bulk dates, portfolios, workflow design, or reporting impact.\n\nThe advanced skill is the safety and decision policy; it does not mean every advanced action uses the `asana-team` server.\n\n- Use `asana-team` only for list teams, update team, create team, add team member, remove team member, and list team members.\n- Use `asana` for supported task, project, section, project-status, dependency, and related project operations.\n- If neither PAT-authenticated route exposes the required operation, stop and report the missing capability. Do not fall back to a Jack-authenticated connector.\n\n## Advanced Work Boundary\n",
  ],
]);
