# 2026-06-12 - VPS1 OpenAI Billing Route Diagnosis

Date | Author | Status: 2026-06-12 | Cody | Diagnosis Complete

## Summary

- Investigated OpenAI usage dashboard jumps and whether VPS1 OpenClaw agents are using Codex/OAuth or direct OpenAI API billing.
- Confirmed all eleven active VPS1 agent containers were healthy during the check.
- Confirmed every active agent container currently has an `OPENAI_API_KEY` present in the runtime environment, so direct API fallback remains technically possible.
- Confirmed current model routing is mixed across agents:
  - `openai/gpt-5.5` primary with `openai/gpt-5.4-mini` fallback: Amanda, Gohzed, Inga, Maggie, Marsha, Victor.
  - `codex/gpt-5.5` primary with `codex/gpt-5.4-mini` fallback: Grogar, Terry, Vivian, Wilma.
  - `openai-codex/gpt-5.5` primary with `openai/gpt-5.5` fallback: Edith.
- Confirmed prior same-day tracking says `openclaw doctor --fix` moved several agents to `openai/gpt-*` to restore Codex Apps Notion connector access, so `openai/gpt-*` alone is not proof of API billing.

## Diagnosis

- The billing-risk condition is the combination of:
  - an OpenAI API key present in the container,
  - an API-key backup auth profile,
  - mixed model/provider naming,
  - and stale or fallback session routing.
- Marsha and Maggie being set to `gpt-5.4-mini` in the control panel does not prove new API usage should appear immediately. Existing sessions can retain older route pins, and OpenAI dashboard views can lag or aggregate by project/model.
- The OpenAI usage dashboard should be filtered by project, model, and tier before drawing conclusions.

## Recommended Next Step

- Test one agent first, preferably Marsha because she was already used for the mini-model test.
- Temporarily remove or disable the API-key fallback for that one agent only.
- Keep the Codex/OAuth route active, restart or reset the one active session, and run a controlled prompt.
- Verify agent logs/tool access and OpenAI dashboard/API-key usage before rolling the same change across the fleet.
- If the one-agent test passes, repeat for Maggie, Amanda, Gohzed, Inga, Victor, and then clean up Edith's `openai/gpt-5.5` fallback.

## Status

- No OpenClaw configs were changed.
- No containers were restarted.
- Notion journal record created: `2026-06-12 | Cody | VPS1 OpenAI Billing Route Diagnosis`.
