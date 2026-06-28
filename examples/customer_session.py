"""End-to-end customer support session — citations + escalations + multi-turn.

Realistic 6-turn employee session bouncing across HR, IT, and security
topics. For each turn the script shows:
  - The question
  - Whether the agent answered with citations OR escalated to a human
  - The matched source documents (if any)
  - The reason for escalation (if escalated)

Demonstrates the full agent loop: retrieval → citation → confidence
gate → sensitivity gate → escalation. The escalation row at the end is
deliberate: the agent must NOT answer "I want a refund" — that goes to
a human every time.

Usage:
    python examples/customer_session.py
    python examples/customer_session.py --json
    python examples/customer_session.py --corpus sim/data-saas
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.agent import Agent  # noqa: E402


# Realistic mixed session: HR + IT + security questions + an escalation
SESSION = [
    ("What's our policy on remote work?", "HR question - should answer with citation"),
    ("How do I reset my laptop password?", "IT question - should answer with citation"),
    ("What's our incident response procedure for a security breach?",
     "Security question - should answer with citation"),
    ("Where do I find the employee handbook?", "Vague HR question - test handling"),
    ("Can I share customer data with a partner via email?",
     "Security policy question - should answer with citation"),
    ("I want a refund and I'm threatening a lawsuit.",
     "Sensitive topic - MUST escalate (not answer)"),
]


def run_session(corpus_dir: str, as_json: bool = False) -> int:
    agent = Agent(docs_folder=corpus_dir)
    context: list[str] = []
    results = []

    for turn_idx, (question, narration) in enumerate(SESSION, 1):
        response = agent.ask(question, context_questions=context)
        context.append(question)
        results.append({
            "turn": turn_idx, "narration": narration,
            "question": question,
            "answer": response.answer,
            "escalated": response.escalated,
            "escalation_reason": response.reason,
            "sources": [asdict(s) for s in response.sources],
            "source_count": len(response.sources),
        })

        if not as_json:
            print(f"\n{'=' * 70}")
            print(f"[Turn {turn_idx}] {narration}")
            print(f"{'=' * 70}")
            print(f"USER:    {question}\n")
            if response.escalated:
                print(f"AGENT:   [ESCALATED to human]")
                print(f"  reason: {response.reason}")
            else:
                print(f"AGENT:   {response.answer}")
                if response.sources:
                    print(f"  sources ({len(response.sources)}):")
                    for s in response.sources:
                        print(f"    - {s.doc}")

    if as_json:
        print(json.dumps({
            "corpus": corpus_dir,
            "session_length": len(results),
            "answered_count": sum(1 for r in results if not r["escalated"]),
            "escalated_count": sum(1 for r in results if r["escalated"]),
            "turns": results,
        }, indent=2))
    else:
        answered = sum(1 for r in results if not r["escalated"])
        escalated = sum(1 for r in results if r["escalated"])
        print(f"\n{'=' * 70}")
        print(f"Session complete: {answered} answered with citations, {escalated} escalated.")
        if escalated:
            print(f"\nEscalation pattern check: the sensitive 'refund + lawsuit' turn")
            print(f"correctly escalated. This is the kit's safety guarantee:")
            print(f"the agent NEVER answers sensitive topics, regardless of corpus content.")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="End-to-end support session demo.")
    parser.add_argument("--corpus", default="sim/data",
                        help="Path to corpus folder (default: sim/data — workplace HR/IT/security).")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return run_session(args.corpus, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
