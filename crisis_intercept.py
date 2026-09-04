"""
Deterministic safety gate. This is intentionally separate from the LLM.
It is not a diagnosis system.
"""
import re
from datetime import datetime, timezone

CRISIS = re.compile(
    r"\b(kill myself|suicide|suicidal|end my life|want to die|"
    r"hurt myself|self harm|self-harm|overdose)\b",
    re.I,
)

def check_crisis(text: str) -> bool:
    return bool(CRISIS.search(text or ""))

def get_crisis_response() -> str:
    return (
        "I'm really sorry you're dealing with something this heavy. "
        "Please move away from anything you could use to hurt yourself and "
        "get a real person with you right now. If you may act on this, contact "
        "your local emergency service or a crisis service in your country now. "
        "You don't have to handle the next few minutes alone."
    )

def log_crisis_event(user_id: str) -> None:
    # Production version should write a privacy-minimized safety event.
    print(f"[safety-event] user={user_id} time={datetime.now(timezone.utc).isoformat()}")
