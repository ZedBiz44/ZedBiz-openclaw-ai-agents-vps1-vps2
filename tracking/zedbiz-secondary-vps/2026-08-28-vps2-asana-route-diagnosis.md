# VPS2 Asana Route Diagnosis: Harry, Suzy, and Frank

date: 2026-08-28 MDT | agent: Manus | status: Diagnosed, no changes made

## Straight Answer

Harry, Suzy, and Frank do **not** have a working agent-specific, PAT-backed Asana route. Nothing recently broke. The route was never included in the original VPS2 build or the later VPS2 update process. In plain language, all three agents have the OpenClaw application running, but none has the secure Asana connection that lets the application talk to Asana as that specific agent.

> A **PAT** is an Asana Personal Access Token. Think of it as a unique key for one agent. A PAT-backed route is a protected connection that uses that agent’s own key, not Jack’s key and not another agent’s key. Before any task is changed, the new Skill asks Asana, “Who am I?” and “Which workspace am I in?” That prevents an agent from accidentally acting as the wrong person.

The VPS1 agents received this type of protected connection during the VPS1 Asana HTTP sidecar rollout. The VPS2 agents did not. Copying the new Skill into Harry, Suzy, or Frank today would not create an Asana connection. It would simply make the Skill stop safely when it cannot complete its required identity check.

## What the Live Check Found

The live check on 2026-08-28 MDT was read-only. It did not alter services, files, skills, accounts, tokens, or Asana data.

| Agent | OpenClaw service | Current version | Configured OpenClaw MCP servers | Asana environment variable names | Asana Skill path | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Harry | Active | 2026.7.1 | None | None | None | No Asana route or Skill |
| Suzy | Active | 2026.7.1 | None | None | None | No Asana route or Skill |
| Frank | Active | 2026.7.1 | None | None | None | No Asana route or Skill |

There is also no active host-level Asana service or process on VPS2. The three agents run as separate native systemd services, not Docker containers. That is intentional for VPS2 and is not itself a problem. The missing piece is the per-agent Asana integration layer.

## What a Working Setup Needs

A safe working setup has four pieces. VPS2 currently has none of the Asana-specific pieces.

| Piece | What it does | VPS2 today |
| --- | --- | --- |
| Agent-specific Asana PAT | Lets the agent access only its own Asana account and permissions | Not configured for Harry, Suzy, or Frank |
| Local Asana MCP service | Converts OpenClaw requests into controlled Asana calls | Not installed or running |
| OpenClaw MCP route named `asana` | Tells the agent where its local Asana service lives and how to authenticate to it | Missing from all three `openclaw.json` files |
| `z-asana-agent-control` Skill | Enforces identity, workspace, scope, and task-action rules | Not installed on VPS2 |

On VPS1, the standard service exposes a controlled tool set including `asana_get_user`, `asana_get_my_tasks`, task reads, comments, and task updates. The first tool is critical. It is how the Skill confirms that an agent is using its own account before it reads or changes any work. The live VPS1 sidecar checks showed 76 tools and passed that identity test for the current cohort.

## What Happened, When, and Why

### Harry

Harry was cleanly rebuilt on **2026-05-25**. The rebuild established per-agent state, 1Password handling for the model provider, HTTPS, systemd service isolation, and an OpenClaw workspace. It did not include Asana, an Asana PAT, an Asana MCP server, or an Asana Skill. That is clear in the original build record. [1]

### Frank

Frank was created on VPS2 on **2026-06-10** by reusing Edith’s former VPS2 service slot. His workspace identity files were created, but the creation record explicitly describes MCP servers as none. The work was a new-agent setup and DNS cutover, not an Asana integration rollout. [2]

### Harry and Suzy updates

On **2026-06-11**, the VPS2 standard update process was validated on Frank and then applied to Harry and Suzy. That process installed or updated only OpenClaw core, the Codex package, and the Discord package. The shared curated-tool installer lists only `@openclaw/codex` and `@openclaw/discord`. Asana was not part of that design. [3] [4]

### Later VPS2 maintenance

On **2026-06-19**, all three VPS2 agents were updated again for model and OpenAI OAuth compliance. Harry and Suzy had model and authentication settings corrected. Frank had an old Codex authentication file removed. The record lists the files touched and does not add an Asana route, PAT, or Asana Skill. [5]

### The separate VPS1 rollout

The persistent Asana HTTP MCP system was rolled out on **VPS1** on **2026-07-29**. It was an explicitly VPS1-only Docker-sidecar deployment. Its goal was to give VPS1 agents a persistent PAT-authenticated Asana service and prevent a separate short-lived Asana process from being spawned on every agent turn. [6]

That explains the current situation. VPS1 has an Asana lane because a dedicated project built one there. VPS2 has no Asana lane because its build and maintenance procedures never contained that project. It was not missed during a VPS2 Asana rollout. There was no VPS2 Asana rollout.

## Why I Did Not Copy the Skill to Harry

The new Skill is a rulebook. It is not the connection itself. Installing the rulebook without the connection would be like putting safe-driving instructions in a truck that has no fuel line. The instructions are fine, but the truck still cannot go anywhere.

More importantly, the Skill is deliberately designed to stop if it cannot verify the agent’s actual Asana identity and required ZedBiz workspace. That would protect you from accidental wrong-account work, but it would also mean Harry could not carry out normal Asana tasks. Installing it first would create a confusing, non-working setup and make the agent look broken when the missing infrastructure is the real issue.

## Safe Fix Plan

VPS2 should keep its native systemd architecture. There is no good reason to install Docker simply to imitate VPS1. The current standard Asana MCP application can run as a small local Node service on VPS2. It exposes `/mcp` and `/healthz`, requires an Asana PAT plus a separate internal bearer secret, and can be kept bound to loopback only. [7] [8]

The safest approach is to handle **Harry first**, then Suzy and Frank only after Harry works. The implementation would do the following.

| Step | What would be done | Why it matters |
| --- | --- | --- |
| Confirm account identity | Confirm the intended Asana email and user GID for Harry. Do not use Jack’s PAT. | Ensures Harry acts only as Harry. |
| Store two agent-scoped secrets | Put Harry’s Asana PAT and a separate internal MCP bearer secret in the approved secret store. | Prevents credentials from being written into Git, the Skill, or plaintext configuration. |
| Install one local service | Install the standard Asana HTTP MCP application under a tracked VPS2 path and run it as one small Harry-specific systemd service on loopback. | Creates the protected fuel line between Harry and Asana without exposing a public port. |
| Add one OpenClaw route | Add a managed MCP server called `asana` to Harry’s `openclaw.json`, pointing only to Harry’s local service with the required authorization header. | Lets Harry reach only his own Asana service. |
| Test read-only first | Check service health, tool inventory, `asana_get_user`, expected email, expected GID, expected workspace, and assigned-task discovery. | Proves that no account mix-up exists before task writes are allowed. |
| Install the Skill | Install `z-asana-agent-control`, remove any legacy artifacts if they exist, restart Harry, and check discovery. | Adds the rulebook after the connection has passed its safety test. |
| Test one approved task workflow | Use a specific safe test task with Jack’s approval. | Confirms the full agent behavior, not just the plumbing. |
| Repeat for Suzy then Frank | Create separately scoped routes and repeat the same tests one agent at a time. | Prevents one account or configuration from bleeding into another. |

The current MCP routing pattern used by the standard implementation is a local URL like `http://<agent>-asana-mcp:8080/mcp` plus an authorization header. VPS2 would use the equivalent loopback-only native service URL on a unique local port for each agent. The OpenClaw configuration must not contain a copied token from another agent. [8]

## What I Need Before Action

No change should be made until you approve this specific plan. Before deploying Harry, I need confirmation of the intended Harry Asana identity and whether its existing PAT is already stored in the approved secret store. If it is not, the missing prerequisite is not a script. It is an agent-specific Asana account credential, created or supplied by the authorized account owner.

Once Harry passes the read-only test, Suzy and Frank should not automatically inherit his credential. Each needs its own identity confirmation and its own scoped credential. If they do not need to work in Asana, the safest and simplest option is to leave their Asana route absent.

## References

[1]: https://github.com/ZedBiz44/zedbiz-ai-agents/blob/main/tracking/zedbiz-secondary-vps/harry-rebuild-2026-05-25.md "Harry VPS2 rebuild record"
[2]: https://github.com/ZedBiz44/zedbiz-ai-agents/blob/main/tracking/zedbiz-secondary-vps/2026-06-10-edith-to-vps1-frank-setup-vps2.md "Frank VPS2 creation record"
[3]: https://github.com/ZedBiz44/zedbiz-ai-agents/blob/main/tracking/zedbiz-secondary-vps/2026-06-11-curated-vps2-installer-script-installed.md "VPS2 curated installer record"
[4]: https://github.com/ZedBiz44/zedbiz-ai-agents/blob/main/tracking/zedbiz-secondary-vps/2026-06-11-harry-suzy-openclaw-update.md "Harry and Suzy update record"
[5]: https://github.com/ZedBiz44/zedbiz-ai-agents/blob/main/tracking/zedbiz-secondary-vps/2026-06-19-vps2-dreams-check-sop-compliance-fix.md "VPS2 all-agent compliance record"
[6]: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/blob/main/ai-agent-sops/zedbiz-main-vps/tracking/2026-07-29-vps1-fleet-asana-http-rollout.md "VPS1 Asana HTTP MCP rollout"
[7]: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/blob/main/docker/asana-http-mcp/README.md "Standard Asana MCP requirements"
[8]: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/blob/main/docker/asana-http-mcp/deploy/fleet/switch-openclaw-mcp.mjs "Standard OpenClaw Asana route pattern"
