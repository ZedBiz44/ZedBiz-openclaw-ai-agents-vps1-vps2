## Hindsight Exact Facts And Source Links

- Do not bury exact identifiers, complete URLs, legal or financial figures, or other values that must be reproduced verbatim inside a long conversation memory.
- Use `agent_knowledge_ingest`, or the platform's Hindsight document-ingest equivalent, to create one small atomic document per exact value.
- Give the document a stable title and document ID. State that the value is exact and must be returned verbatim.
- Store the authoritative source URL, record type, agent, source system, and next action as metadata when the integration supports it.
- During recall, verify the exact value against returned metadata, the document ID, or the authoritative source before acting.
- Keep narrative auto-retain for context, preferences, decisions, and lessons; use atomic documents for verbatim facts.
