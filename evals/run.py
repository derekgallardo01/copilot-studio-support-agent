"""Run the agent against the golden evaluation set and report pass/fail.

    python evals/run.py

Exit code is 0 if all cases pass, 1 otherwise — suitable for CI gating.
The golden set lives next to this file as `golden.json`.
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


def main() -> int:
    with open(os.path.join(HERE, "golden.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    docs = os.path.join(os.path.dirname(HERE), "sim", "data")
    agent = Agent(docs)
    result = evaluate(cases, agent)

    total = len(cases)
    n_pass = len(result["passed"])
    n_fail = len(result["failed"])
    rate = (n_pass / total * 100) if total else 0.0
    print(f"Eval: {n_pass}/{total} passed ({rate:.0f}%)")
    if n_fail:
        print(f"\n{n_fail} failed:")
        for f in result["failed"]:
            print(f"  [{f['id']}] {f['question']}")
            for d in f["details"]:
                print(f"      {d}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
