---
name: zedbiz-advanced-asana-control
description: Use only for approved top-level ZedBiz Asana agents such as Amanda, Marsha, and Ruby when managing Asana projects, status updates, project briefs, custom fields, sections, task ordering, dependencies, blockers, bulk date shifts, and higher-level Asana workflow improvements. Requires PAT-based identity verification and confirmation gates for risky or structural changes.
---

# ZedBiz Advanced Asana Control

Use this skill only for approved top-level Asana agents: Amanda, Marsha, Ruby, or another agent explicitly approved by Jack.

This is not the regular daily task execution skill. Regular agents use `zedbiz-asana-agent-control`.

## Required Preflight

Before advanced Asana work:

- Call the standard PAT MCP `asana_get_user` tool with `user_gid: "me"`.
- Confirm authenticated email matches the agent's Asana email.
- Confirm workspace GID.
- Confirm target project/task/section/custom field GIDs.
- Confirm the agent has permission for the operation.
- Confirm Get-er-Done Mode or Diagnose Mode.

If identity resolves to Jack through Codex/ChatGPT connector, stop unless Jack explicitly requested admin lookup.

Treat a successful PAT-backed identity call as authoritative. Do not block solely because `openclaw mcp probe asana` reports HTTP/SSE 400 against a Streamable HTTP service.

## Blast Radius

- One task: normal or risky depending on fields, dates, dependencies, and client impact.
- One project: Diagnose Mode unless the change is trivial.
- Multiple projects, workspace, dashboards, or reporting: explicit Jack confirmation.

## Automatic Skill And Tool Routing

- Load this skill automatically for team administration, portfolio changes,
  workspace custom-field administration, goals administration, webhooks,
  workload allocations, templates, organization operations, unrestricted
  public-API work, and broad structural changes.
- Amanda and Marsha use one `asana` route backed by the 126-tool Asana Advanced
  HTTP MCP. It is a complete superset of Standard; there is no separate
  `asana-team` route.
- Verify identity once through `asana_get_user`, then prefer the named tool that
  matches the operation.
- Use `asana_api_request` only when no named tool covers a supported public Asana
  API endpoint. It is not a shortcut around confirmation, permissions, or
  safety controls.
- The route uses the agent's own PAT. The available authority is therefore the
  intersection of this toolset, Asana's public API, the agent's Asana account
  permissions, and the ZedBiz approval rules in this skill.

## Advanced Work Boundary

This skill may handle every Standard operation plus team administration,
portfolio creation and structure, project setup and cleanup, project briefs,
project status updates, custom-field systems, goals, sections and task ordering,
dependencies and blockers, bulk date shifts, timeline changes, templates,
webhooks, allocations, exports, audit reads when the Asana plan and credential
allow them, and cross-agent Asana coordination.

It does not silently delete, archive, or restructure major systems. Ask first.

Asana's public API does not provide general creation or editing of native Rules
or dashboard layouts. The toolset can trigger an existing incoming-web-request
rule and can perform all supported public API operations, but it must never
claim that unsupported UI-only control exists.

Read the current structure before cleanup, workflow changes, sections, fields, dependencies, or reporting edits.

No silent schema changes: preview custom fields, sections, templates, portfolios, and reporting structures before changing them.

## Project Status Updates

Use for project progress, blockers, risks, next actions, owner/agent responsibility, and executive visibility. Do not post if project facts were not verified.

Draft before posting unless Jack or the task explicitly says to publish live.

## Project Briefs

Briefs should cover business outcome, scope, non-scope, key people/agents, workflow sections, custom fields, reporting expectations, and related Notion/GitHub links.

Draft before publishing or replacing an existing brief unless Jack or the task explicitly says to publish live.

## Custom Fields

Enumerate fields and enum option GIDs before changing anything. Confirm whether fields are local, library/global, or connected to reporting. Use Diagnose Mode for system-level field changes.

## Sections And Task Ordering

Read existing sections first, preserve current workflow unless redesign is requested, use section GIDs, and use insert_before/insert_after where supported. Avoid mass moves without confirmation.

## Dependencies And Blockers

Add dependencies only when real. Remove dependencies only when resolved or confirmed. Escalate cross-agent blockers clearly.

## Bulk Date Shifting

Never shift dates without preview. Run dry run first, review affected tasks, ask for confirmation when more than one task/project is affected, then commit.

## Rollback Plan

Before broad edits, note how to reverse or repair the change. For bulk updates, capture the affected task/project list before committing.

## Confirmation Rules

Ask Jack before deleting, archiving, bulk editing, bulk shifting dates, changing custom field systems, creating/redesigning workflows, changing dependencies in bulk, or affecting multiple projects/agents.

Stop and ask Jack on client-facing, destructive, permission, workflow, reporting, portfolio, or large-scale changes.

## Approval Matrix

- Read/inspect: allowed after identity preflight.
- Draft status/brief/recommendation: allowed.
- Post status/brief: allowed only when requested or approved.
- Single project structural change: Diagnose Mode and confirmation.
- Bulk or cross-project change: dry run plus explicit confirmation.
- Delete/archive/schema/reporting change: explicit confirmation every time.

## Logging

After advanced changes, add an Asana comment/status note and log major work in Notion Tech Updates and GitHub where available. Major means structural changes, bulk updates, project status/brief edits, custom field changes, portfolio changes, or anything affecting dashboards/reporting. Use Mountain Time.
