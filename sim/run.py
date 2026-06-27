"""Demo the agent: grounded answers with citations + escalation."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import Agent  # noqa: E402

QUESTIONS = [
    "How do I reset my password?",
    "How many PTO days do new employees get?",
    "Who do I contact about a security incident?",
    "I want a refund on my subscription",          # sensitive → escalate
    "What is the airspeed velocity of an unladen swallow?",  # low confidence → escalate
]


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    agent = Agent(os.path.join(here, "data"))
    for q in QUESTIONS:
        r = agent.ask(q)
        print(f"\nUSER: {q}")
        if r.escalated:
            print(f"AGENT → 🤝 escalated ({r.reason}): {r.answer}")
        else:
            cites = ", ".join(f"[{i+1}] {s.doc}" for i, s in enumerate(r.sources))
            print(f"AGENT: {r.answer}\n       sources: {cites}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
