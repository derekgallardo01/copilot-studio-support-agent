# FAQ

## Do I need API keys to run this?

No. The default generator (`_stub_answer` in `sim/agent.py`) is
deterministic and uses only the Python standard library. The
Azure OpenAI / Anthropic adapters are wired but only fire when you set
`LLM_PROVIDER=azure` or `=anthropic` plus the matching credentials —
[customization.md §4](customization.md#4-plug-a-real-llm) covers it.

## Why TF-IDF and not embeddings?

For the kinds of corpora a typical internal Copilot Studio agent sees
(hundreds to low thousands of policy chunks), TF-IDF is fast, deterministic,
and trivially explainable. It also works without a model server, which
makes the demo runnable in 30 seconds. For larger corpora or genuinely
fuzzy semantic match you'd swap the `Retriever` for an embeddings-based
one — the rest of the agent doesn't change.

## How does the "sensitive topic" check work?

Substring scan against a `SENSITIVE` tuple in `sim/agent.py`. The Copilot
Studio production version uses Topics with trigger phrases; the
declarative template in `agent-template/topics.json` mirrors the same
list. Sensitive checks always run on the **bare current question**, never
the concatenated multi-turn context — so a benign follow-up can't
accidentally bypass an escalation.

## Can the agent answer questions across multiple documents?

Yes. The default `k=2` retrieves the top two chunks (across all
documents) and the answer is composed from both, with `[1]` and `[2]`
citations. To return more or fewer sources, change `k` in the
`Agent.ask()` call.

## What happens when the corpus is updated?

The simulator re-indexes on every `Agent(...)` construction. A long-
running deployment that adds documents needs to either re-instantiate the
agent or extend the `Retriever` with an incremental update method. In the
real Copilot Studio path, the SharePoint indexer handles re-indexing
on a schedule.

## How do I add a new escalation rule?

Edit `SENSITIVE` in `sim/agent.py` to add the keyword(s). Mirror in
`agent-template/agent.yaml` under `sensitive_topics`. Add a case to
`evals/golden.json` with `expect.escalated: true, expect.reason:
"sensitive topic"`. Re-run `python evals/run.py` to confirm it fires
and doesn't break existing cases.

## Why does the multi-turn `Conversation` re-inject context only sometimes?

If we always re-injected the prior question, strong-signal queries would
get polluted by unrelated earlier topics (e.g. "what's the PTO policy?"
followed by "how do I reset my password?" — the password question would
inherit "PTO" tokens). The wrapper only re-runs with context when the
bare query returns low confidence, which is precisely when an inherited
context actually helps. See `sim/conversation.py` for the 5-line check.

## Where do the live-demo screenshots come from?

`.github/workflows/screenshots.yml` (manual trigger). It spins up
Playwright + Chromium in CI, navigates to the live Pages demo, captures
PNGs at 1280×800 @ 2x scale, and commits them back to `docs/screenshots/`.
The README references those committed files.

## Is this safe to put on real PII?

The simulator itself just reads files you point it at. The Copilot
Studio production path needs the M365 privacy / DLP / data-residency
configuration captured separately — see
[m365-privacy-config](https://github.com/derekgallardo01/m365-privacy-config)
for the checklist.
