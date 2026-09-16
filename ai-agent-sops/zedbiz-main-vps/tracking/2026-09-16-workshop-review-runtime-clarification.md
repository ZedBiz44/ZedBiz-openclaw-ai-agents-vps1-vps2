# Workshop Review Runtime Clarification

> 2026-09-16 | Cody | Status: Diagnosed; live repair awaiting Jack's approval

## Scope

The rooted-runtime error applies to two weekly jobs:

- Scheduled main-agent cleanup
- Scheduled email-helper cleanup

It does not apply to the after-conversation review. That review starts only after an eligible foreground turn reaches at least 10 model iterations and the system is idle for 30 seconds. It reuses that conversation's provider, model, authentication, and runtime with fallbacks disabled.

## Plain-language runtime definition

- The model is the AI doing the thinking.
- Authentication is the account permission used to reach that model.
- The execution runtime is the software runner that manages one turn, sends the prompt, handles tool calls, and returns the result.
- `codex` means Codex app-server runs the turn.
- `openclaw` means OpenClaw's embedded runner runs the turn.

The word runtime does not mean that the task runs forever. It identifies which runner controls that particular turn.

## Weekly cleanup requirement

Weekly cleanup can edit Workshop skills, so its file tools must be locked to the selected identity's Workshop directory. OpenClaw calls these rooted tools. The Codex app-server runtime is not supported for this weekly rooted review. A compatible OpenClaw-controlled runtime must run the job.

Authentication and runtime are separate. OpenClaw's embedded runner can use an `openai/*` model through the selected OpenAI OAuth profile. This is why Terry's cleanup used OpenAI Terra successfully even though OpenClaw, rather than Codex app-server, controlled the turn.

## Current fleet behavior

- Normal WebUI, Discord, and Telegram conversations remain on the native Codex runtime for Terry, Vivian, and the other Codex-primary agents.
- Terry and Vivian differ only in their fallback map: Terra and Luna can run under the OpenClaw embedded runtime when a rooted weekly cleanup rejects the Codex primary.
- Twelve agents lack that compatible OpenAI fallback: Amanda, Edith, GoZed, Grogar, Inga, Maggie, Marsha, Victor, Wilma, Harry, Suzy, and Frank.
- Rocky uses Grok for this path and is separate.
- One runtime-map correction per affected OpenClaw installation covers both its main identity and its `mail_reader` identity because both inherit that installation's model map.

## Saved empty-folder results

Thirteen recorded empty-folder weekly cleanups succeeded:

- 11 used Gemini through OpenClaw's embedded runner.
- Terry's main-agent cleanup used OpenAI Terra through OpenClaw's embedded runner.
- Rocky's email-helper cleanup used Grok through an OpenClaw-controlled runner.

Maggie's failed main-agent cleanup also used Gemini through OpenClaw. It listed the empty Workshop correctly, then made one unnecessary parent-folder request that OpenClaw blocked. Three exact unchanged reruns used Gemini and returned `NO_REPLY`. The model choice explains why Gemini was present; the single extra tool choice explains why only that run failed.

## Recommended repair

- Keep normal primary models on Codex for conversations.
- Give each affected installation a compatible OpenAI fallback that runs under OpenClaw for the two scheduled weekly cleanups.
- Use Terra, then Luna, for Astra- and Sol-primary agents.
- For Wilma, keep primary Terra on Codex and use Luna as the rooted OpenAI fallback.
- Leave Terry, Vivian, and Rocky unchanged.
- Test both Maggie's scheduled main-agent cleanup and scheduled email-helper cleanup. Confirm OpenAI handled both through the OpenClaw runner and neither reached Gemini.
- After Jack reviews the receipts, apply the same configuration pattern to the remaining affected agents.

No live agent configuration was changed during this clarification.
