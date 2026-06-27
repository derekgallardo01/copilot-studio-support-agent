import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from agent import Agent  # noqa: E402
from conversation import Conversation  # noqa: E402

AGENT = Agent(os.path.join(os.path.dirname(HERE), "data"))


def _fresh():
    return Conversation(AGENT)


def test_conversation_records_turns():
    conv = _fresh()
    conv.ask("how do I reset my password?")
    conv.ask("how many PTO days do I get?")
    assert len(conv.history()) == 2
    assert conv.history()[0].response.sources[0].doc == "it-support.md"
    assert conv.history()[1].response.sources[0].doc == "hr-policy.md"


def test_reset_clears_context():
    conv = _fresh()
    conv.ask("how do I reset my password?")
    conv.reset()
    assert conv.history() == []


def test_sensitivity_check_uses_current_question_only():
    # Prior benign turn must not mask a sensitive follow-up.
    conv = _fresh()
    conv.ask("what are the working hours?")
    r = conv.ask("I want a refund on my subscription")
    assert r.escalated and r.reason == "sensitive topic"


def test_followup_inherits_context_for_retrieval():
    # A bare follow-up like "what about for managers?" has no useful tokens on its
    # own; the window should let it still route to the right doc.
    conv = _fresh()
    conv.ask("how many PTO days do new employees get?")
    r = conv.ask("what about for managers?")
    assert not r.escalated
    assert r.sources and r.sources[0].doc == "hr-policy.md"
