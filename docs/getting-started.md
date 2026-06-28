# Getting started

A 5-minute walkthrough that takes you from `git clone` to "I can see it
work" — no LLM keys, no Microsoft 365 tenant, no `pip install` other than
pytest if you want to run the tests.

## 1. Clone and run the demo

```bash
git clone https://github.com/derekgallardo01/copilot-studio-support-agent.git
cd copilot-studio-support-agent
python sim/run.py
```

You should see five Q&A pairs printed. The first three are grounded
answers with citations to `it-support.md`, `hr-policy.md`, and
`security.md`. The fourth (a refund question) escalates as a sensitive
topic. The fifth (a nonsense question) escalates as low confidence.

## 2. Run the eval set

```bash
python evals/run.py
```

You should see `Eval (golden.json): 16/16 passed (100%)`. This is the
golden Q&A set for the **workplace** corpus. There's a second corpus
(SaaS support) — run it with:

```bash
python evals/run.py golden-saas.json sim/data-saas
```

Expected: `Eval (golden-saas.json): 14/14 passed (100%)`.

## 3. Try the multi-turn REPL

```bash
python sim/cli.py
```

Then try:

```
you> how many PTO days do new employees get?
you> what about for managers?
```

The second question has no useful tokens on its own; the conversation
wrapper re-injects the prior turn into retrieval so it still routes to
the HR doc.

## 4. Run in Docker (optional)

If you don't want to install Python:

```bash
docker build -t copilot-studio-agent .
docker run --rm copilot-studio-agent
```

## What to read next

- [Architecture](architecture.md) — components, data flow, sequence
  diagrams, "where to look first if X breaks"
- [Customization](customization.md) — swap the corpus, tune the
  sensitive-topic list, plug in a real LLM
- [Evaluation](evaluation.md) — how to add a case, the tuning workflow
- [Diagrams](diagrams.md) — additional system + sequence + state diagrams

## Bringing it to a real tenant

The simulator proves the **behaviour**. The matching Copilot Studio
template (`agent-template/agent.yaml` + `topics.json` +
`prompt-library.md`) is what you actually build in the tenant. The
go-live steps are in [`deploy-guide.md`](../deploy-guide.md).
