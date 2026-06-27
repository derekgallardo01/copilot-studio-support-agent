# Customization

Five things you'll typically tune per client. Each is a small, localized change.

## 1. Swap the document corpus

Drop your documents into [sim/data/](../sim/data/) (`.md` or `.txt`). The retriever
indexes everything in the folder on `Agent(...)` construction — no separate build
step.

```python
agent = Agent("path/to/your/docs")
```

For production, the corpus is whatever SharePoint sites/libraries you connect in
[agent-template/agent.yaml](../agent-template/agent.yaml) under
`knowledge_sources`.

## 2. Tune the sensitive-topic list

Edit `SENSITIVE` in [sim/agent.py](../sim/agent.py):

```python
SENSITIVE = ("refund", "cancel my account", "legal", "lawsuit", "complaint",
             "data breach", "gdpr", "termination", "salary dispute",
             # add client-specific topics:
             "medical claim", "credit limit increase")
```

The matching is a substring scan on the lowercased question — simple on purpose so
you (or a non-engineer client owner) can edit it without breaking anything. Mirror
the same list in `sensitive_topics:` in [agent-template/agent.yaml](../agent-template/agent.yaml)
so the production Copilot Studio agent matches.

## 3. Adjust the confidence threshold

`MIN_CONFIDENCE = 0.05` in [sim/agent.py](../sim/agent.py). Below this score the
agent escalates instead of guessing.

- **Higher value (e.g. 0.10)** → fewer guesses, more escalations. Use for
  regulated / customer-facing deployments.
- **Lower value (e.g. 0.02)** → more answers, more risk. Use for internal-only
  pilots where escalation friction is a problem.

The right value depends on your corpus — run [evals/run.py](../evals/run.py)
after each change to see the impact.

## 4. Plug a real LLM

The retrieval / escalation flow is intentionally model-free; only the answer
*generation* step uses a stub today (`_stub_answer` in [sim/agent.py](../sim/agent.py)).
Swap it for a real model behind one `complete(prompt) -> str` interface:

```python
def _stub_answer(q, hits):
    passages = "\n\n".join(f"[{i+1}] {s.text}" for i, (s, _) in enumerate(hits))
    prompt = (
        "Answer the question using ONLY the passages below. Cite sources as [n]. "
        "If the answer isn't in the passages, say you don't know.\n\n"
        f"Passages:\n{passages}\n\nQuestion: {q}"
    )
    return your_llm_client.complete(prompt)
```

The prompt template that matches Copilot Studio's behaviour is in
[agent-template/prompt-library.md](../agent-template/prompt-library.md) under
"Grounded-answer pattern". Use the same wording in both places so simulator
behaviour matches production.

## 5. Add a new intent / topic

In production, intents are Copilot Studio Topics. The simulator's equivalent is
either a small classifier in front of `Agent.ask()` or — for routing-only intents
— extending the early-return pattern:

```python
GREETINGS = ("hi", "hello", "hey")
def ask(self, question, ...):
    if question.strip().lower() in GREETINGS:
        return AgentResponse(answer="Hi! What can I help with?", sources=[], escalated=False)
    if _is_sensitive(question):
        ...
```

Mirror new intents in [agent-template/topics.json](../agent-template/topics.json) so
the design carries to the tenant.

## Validating any change

After any of the above, re-run the gold tests:

```bash
python -m pytest sim/tests/ -q
python evals/run.py
```

If you change the corpus or the sensitive list, add new cases to
[evals/golden.json](../evals/golden.json) **before** changing the code. That's
how regressions stay visible.
