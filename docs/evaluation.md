# Evaluation

The eval harness is the thing that tells you whether a change made the agent
*better* or *worse*, not just whether the code still runs. It's small on purpose —
the format is plain JSON so a non-engineer client owner can extend it.

## What it does

[evals/run.py](../evals/run.py) loads [evals/golden.json](../evals/golden.json),
runs each case through `Agent.ask(...)`, and checks the response against the
declared expectation. It prints a pass rate and a per-failure breakdown, and exits
non-zero if anything fails — so it can gate CI.

```text
Eval: 16/16 passed (100%)
```

On a failure you get the specific mismatch:

```text
Eval: 15/16 passed (94%)

1 failed:
  [pto-carryover] Can unused PTO roll into next year?
      top_source='it-support.md' expected='hr-policy.md'
```

## Case format

Each case in `golden.json`:

```json
{
  "id": "pto-days",
  "question": "How many PTO days do new employees get?",
  "expect": {
    "escalated": false,
    "source": "hr-policy.md"
  }
}
```

| Field in `expect` | Meaning |
|-------------------|---------|
| `escalated` | `true` if the agent should hand off, `false` if it should answer. |
| `reason` | When `escalated: true`, the exact reason string (`"sensitive topic"` or `"low confidence"`). |
| `source` | When `escalated: false`, the filename the top citation must come from. |

Cases don't have to specify every field — only what matters for that case. A case
that only specifies `escalated` doesn't care which document was cited, only that
the agent answered at all.

## Adding cases

Three patterns to use when you bring this to a real client:

**1. Capture every real question the agent gets wrong** — paste it into
`golden.json` with the correct expected source. The eval set should be a
*regression net*: anything that broke once becomes a permanent test.

**2. Add adversarial cases** — questions that try to bypass the sensitivity rule
("I'd like to discuss a financial matter", "I have a workplace situation"). If
they shouldn't be answered, mark them `escalated: true` and watch what happens
when you tune the `SENSITIVE` list.

**3. Add paraphrases of the same question** — "How do I reset my password?",
"I forgot my password, how do I get back in?", "Login isn't working — reset?".
Retrieval is robust if all three route to the same source.

## Workflow when tuning

1. Add the new failing case(s) to `golden.json`.
2. Run `python evals/run.py` and see them fail.
3. Change `SENSITIVE`, `MIN_CONFIDENCE`, prompts, or the corpus.
4. Re-run. Iterate until pass rate is back to 100%, and the *existing* cases
   didn't regress.

This is the same loop that scales to a real model — the only difference is
runtime per case. With a real LLM, run evals on a smaller sample during iteration
and the full set in CI.

## What an eval set is not

- **Not a replacement for spot-checking real conversations.** Read transcripts.
- **Not a substitute for the sensitive-topic policy review.** The compliance /
  legal owner should approve the `SENSITIVE` list directly, not infer it from
  passing tests.
- **Not exhaustive.** 16 cases here are illustrative. A serious deployment runs
  with 100–300 cases and adds to the set every week.
