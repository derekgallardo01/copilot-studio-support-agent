"""Interactive REPL for the support agent.

    python sim/cli.py

Commands: 'reset' clears multi-turn context, 'quit' or Ctrl-D exits.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from agent import Agent  # noqa: E402
from conversation import Conversation  # noqa: E402


def _format(r) -> str:
    if r.escalated:
        return f"(escalated, {r.reason}): {r.answer}"
    cites = ", ".join(f"[{i+1}] {s.doc}" for i, s in enumerate(r.sources))
    return f"{r.answer}\n  sources: {cites}"


def main() -> int:
    agent = Agent(os.path.join(HERE, "data"))
    conv = Conversation(agent)
    print("Support agent. Commands: 'reset' clears context, 'quit' exits.\n")
    while True:
        try:
            q = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not q:
            continue
        if q.lower() in {"quit", "exit"}:
            return 0
        if q.lower() == "reset":
            conv.reset()
            print("(context cleared)\n")
            continue
        print(_format(conv.ask(q)) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
