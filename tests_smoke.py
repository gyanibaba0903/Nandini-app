from mood_detector import detect_mood, detect_intent
from conversation_director import build_director_context
from crisis_intercept import check_crisis
from memory_engine import candidate_from_user_text

def test_playful():
    assert detect_mood("haha you're funny") == "playful"

def test_low():
    assert detect_mood("I feel lonely") == "low"

def test_help():
    assert detect_intent("help me plan this", "normal") == "help_requested"

def test_crisis_gate():
    assert check_crisis("I want to kill myself") is True

def test_director_companionship():
    x = build_director_context("u", "I'm bored", "bored", "nandini")
    assert "COMPANIONSHIP" in x

def test_memory_candidate():
    x = candidate_from_user_text("I love cricket")
    assert x and x["type"] == "preference"
