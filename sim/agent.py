"""Offline simulator of a Copilot Studio support agent.

Demonstrates the agent's logic without a tenant: retrieve grounded answers from
SharePoint-style docs with citations, and escalate to a human when confidence is
low or the topic is sensitive. The real agent is built declaratively in Copilot
Studio (see ../agent-template/); this proves the behaviour.

Stdlib-only. The generation step uses a deterministic local stub; a real model
plugs in via LLM_PROVIDER without changing the flow.
"""

from __future__ import annotations

import glob
import math
import os
import re
from collections import Counter
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP = {"a", "an", "the", "is", "are", "of", "to", "in", "for", "on", "and",
        "or", "do", "does", "i", "you", "what", "who", "how", "my", "me", "it",
        "with", "can", "your", "we", "us", "this", "that", "be", "at", "as"}

# Topics the agent must hand to a human rather than answer itself.
SENSITIVE = ("refund", "cancel my account", "legal", "lawsuit", "complaint",
             "data breach", "gdpr", "termination", "salary dispute")
# Below this retrieval confidence, escalate instead of guessing.
MIN_CONFIDENCE = 0.05


def _tok(t: str) -> list[str]:
    return [w for w in TOKEN_RE.findall(t.lower()) if w not in STOP]


@dataclass
class Source:
    doc: str
    text: str


@dataclass
class AgentResponse:
    answer: str
    sources: list[Source]
    escalated: bool
    reason: str = ""


class Retriever:
    def __init__(self, folder: str):
        self.docs: list[Source] = []
        for path in sorted(glob.glob(os.path.join(folder, "*"))):
            if path.lower().endswith((".md", ".txt")):
                with open(path, encoding="utf-8") as fh:
                    self.docs.append(Source(os.path.basename(path), fh.read()))
        n = len(self.docs) or 1
        df: Counter[str] = Counter()
        for d in self.docs:
            df.update(set(_tok(d.text)))
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}

    def _vec(self, tokens):
        tf = Counter(tokens)
        return {t: tf[t] * self.idf.get(t, 0.0) for t in tf}

    def search(self, q: str, k: int = 2):
        qv = self._vec(_tok(q))
        qn = math.sqrt(sum(v * v for v in qv.values())) or 1.0
        out = []
        for d in self.docs:
            dv = self._vec(_tok(d.text))
            dn = math.sqrt(sum(v * v for v in dv.values())) or 1.0
            dot = sum(qv.get(t, 0.0) * w for t, w in dv.items())
            out.append((d, dot / (qn * dn)))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:k]


def _is_sensitive(q: str) -> bool:
    ql = q.lower()
    return any(term in ql for term in SENSITIVE)


def _stub_answer(q: str, hits) -> str:
    parts = []
    for i, (src, _s) in enumerate(hits, 1):
        sents = re.split(r"(?<=[.!?])\s+", src.text.replace("\n", " "))
        qset = set(_tok(q))
        best = max(sents, key=lambda s: len(qset & set(_tok(s))), default="")
        parts.append(f"{best.strip()} [{i}]")
    return " ".join(p for p in parts if p.strip())


class Agent:
    def __init__(self, docs_folder: str):
        self.retriever = Retriever(docs_folder)

    def ask(self, question: str, context_questions: list[str] | None = None) -> AgentResponse:
        # Sensitivity / scope checks always look at the bare current question so prior
        # turns can't accidentally trip or mask the escalation rule.
        if _is_sensitive(question):
            return AgentResponse(
                answer="I'm connecting you with a specialist who can help with this.",
                sources=[], escalated=True, reason="sensitive topic",
            )
        retrieval_query = " ".join((context_questions or []) + [question])
        hits = self.retriever.search(retrieval_query, k=2)
        top_score = hits[0][1] if hits else 0.0
        if top_score < MIN_CONFIDENCE:
            return AgentResponse(
                answer="I don't have a confident answer — let me hand you to a "
                       "team member.",
                sources=[], escalated=True, reason="low confidence",
            )
        return AgentResponse(
            answer=_stub_answer(question, hits),
            sources=[src for src, _ in hits],
            escalated=False,
        )
