import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from agent import Agent  # noqa: E402

AGENT = Agent(os.path.join(os.path.dirname(HERE), "data"))


def test_answers_known_question_with_sources():
    r = AGENT.ask("how do I reset my password?")
    assert not r.escalated
    assert r.sources and r.sources[0].doc == "it-support.md"
    assert "[1]" in r.answer


def test_escalates_sensitive_topic():
    r = AGENT.ask("I want a refund on my subscription")
    assert r.escalated and r.reason == "sensitive topic"


def test_escalates_low_confidence():
    r = AGENT.ask("what is the airspeed velocity of an unladen swallow?")
    assert r.escalated and r.reason == "low confidence"


def test_pto_routes_to_hr():
    r = AGENT.ask("how many PTO days do new employees get?")
    assert not r.escalated
    assert r.sources[0].doc == "hr-policy.md"


def test_deterministic():
    assert AGENT.ask("vpn access").answer == AGENT.ask("vpn access").answer
