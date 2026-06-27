"""Run the agent against a golden evaluation set and report pass/fail.

    python evals/run.py                              # default: golden.json + sim/data
    python evals/run.py golden-saas.json sim/data-saas

Exit code is 0 if all cases pass, 1 otherwise — suitable for CI gating.
Two corpora ship in the repo: the workplace one (HR / IT / Security) under
`sim/data/` and the SaaS support one (product / billing / troubleshooting)
under `sim/data-saas/`. Each pairs with its own golden set.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "sim"))

from agent import Agent  # noqa: E402


def _check(case: dict, response) -> tuple[bool, list[str]]:
    expect = case["expect"]
    details: list[str] = []
    if response.escalated != expect.get("escalated", False):
        details.append(f"escalated={response.escalated} expected={expect.get('escalated', False)}")
    if expect.get("reason") and response.reason != expect["reason"]:
        details.append(f"reason={response.reason!r} expected={expect['reason']!r}")
    if expect.get("source"):
        top = response.sources[0].doc if response.sources else None
        if top != expect["source"]:
            details.append(f"top_source={top!r} expected={expect['source']!r}")
    return (len(details) == 0, details)


def evaluate(cases: list[dict], agent: Agent) -> dict:
    passed, failed = [], []
    for case in cases:
        r = agent.ask(case["question"])
        ok, details = _check(case, r)
        record = {"id": case.get("id", "?"), "question": case["question"], "details": details}
        (passed if ok else failed).append(record)
    return {"passed": passed, "failed": failed}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    golden_name = argv[0] if len(argv) > 0 else "golden.json"
    docs_rel = argv[1] if len(argv) > 1 else os.path.join("sim", "data")

    golden_path = (golden_name if os.path.isabs(golden_name)
                   else os.path.join(HERE, golden_name))
    docs_path = (docs_rel if os.path.isabs(docs_rel)
                 else os.path.join(os.path.dirname(HERE), docs_rel))

    with open(golden_path, encoding="utf-8") as fh:
        cases = json.load(fh)
    agent = Agent(docs_path)
    result = evaluate(cases, agent)

    total = len(cases)
    n_pass = len(result["passed"])
    n_fail = len(result["failed"])
    rate = (n_pass / total * 100) if total else 0.0
    label = os.path.basename(golden_path)
    print(f"Eval ({label}): {n_pass}/{total} passed ({rate:.0f}%)")
    if n_fail:
        print(f"\n{n_fail} failed:")
        for f in result["failed"]:
            print(f"  [{f['id']}] {f['question']}")
            for d in f["details"]:
                print(f"      {d}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
