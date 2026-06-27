# Deploy guide — Copilot Studio agent

Steps to build this agent in a real Microsoft 365 tenant. The simulator in `sim/`
proves the logic; this recreates it in Copilot Studio.

## Prerequisites
- Copilot Studio license + access to the target tenant.
- A SharePoint site/library holding the approved knowledge documents.
- Privacy/data-handling configured per your M365 privacy config (no public-model training,
  data residency, DLP) — do this *first* for regulated clients.

## Steps
1. **Create the agent** — Copilot Studio → Agents → New. Name it, paste the
   `instructions` from `agent-template/agent.yaml`.
2. **Connect knowledge** — add the SharePoint site/libraries as knowledge sources
   (see `knowledge_sources` in the template). Wait for indexing.
3. **Set generative answers** — enable generative mode; set content moderation;
   confirm answers cite sources.
4. **Add escalation topics** — recreate the topics in `agent-template/topics.json`:
   a sensitive-topic handoff and a low-confidence fallback that route to Teams /
   a live agent / a ticket.
5. **Test** — use the questions in `sim/run.py` as a test script: confirm grounded
   answers with citations, and that sensitive/low-confidence questions escalate.
6. **Publish** — to Teams and/or a web chat channel.
7. **Handover** — document in a handover pack and walk the client
   through editing topics and adding knowledge.

## Go-live checklist
- [ ] Knowledge sources indexed and answers cite them.
- [ ] Sensitive topics escalate (don't answer).
- [ ] Low-confidence questions hand off gracefully.
- [ ] Privacy/no-training configuration recorded and signed off (privacy config).
- [ ] Channels published; owner can edit topics.
- [ ] Handover guide + walkthrough delivered (handover pack).
