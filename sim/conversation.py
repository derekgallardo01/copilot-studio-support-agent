"""Multi-turn conversation wrapper around the stateless Agent.

Carries a sliding window of prior user questions into retrieval so follow-ups
like "what about for managers?" work, without changing the escalation rules
(those still look at the bare current question — see Agent.ask).
"""

from __future__ import annotations

from dataclasses import dataclass

from agent import Agent, AgentResponse


@dataclass
class Turn:
    question: str
    response: AgentResponse


class Conversation:
    def __init__(self, agent: Agent, window: int = 3):
        self.agent = agent
        self.window = window
        self.turns: list[Turn] = []

    def ask(self, question: str) -> AgentResponse:
        # Try the bare question first; only fall back to prior context when the
        # current turn is genuinely uncertain. Keeps strong-signal questions from
        # being polluted by an unrelated earlier topic.
        response = self.agent.ask(question)
        needs_context = (
            response.escalated
            and response.reason == "low confidence"
            and len(self.turns) > 0
        )
        if needs_context:
            context = [t.question for t in self.turns[-self.window:]]
            response = self.agent.ask(question, context_questions=context)
        self.turns.append(Turn(question=question, response=response))
        return response

    def reset(self) -> None:
        self.turns.clear()

    def history(self) -> list[Turn]:
        return list(self.turns)
