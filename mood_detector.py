"""
Nandini/Shiv — Mood + Intent Detector V1.1
Mood is a signal, NOT the response strategy.
"""
import re

SAD = re.compile(
    r"\b(sad|depress|lonely|alone|cry|crying|hopeless|worthless|numb|hurt|"
    r"broken|empty|struggl|overwhelm|udaas|a+kela|a+keli|thaka hua|rona)\b"
    r"|koi (boyfriend|girlfriend|dost) nahi|nobody (understands|cares|listens)|"
    r"koi samajhta nahi",
    re.I,
)
PLAYFUL = re.compile(
    r"hahah|\bhaha+\b|\blol\b|\blmao\b|😂|🤣|😆|just joking|i was joking|"
    r"\bjoke\b|kidding|you make me laugh|you are funny|you're funny", re.I
)
BORED = re.compile(r"\bbored\b|\bboring\b|time pass|mann nahi lag|man nahi lag", re.I)
EXCITED = re.compile(
    r"\bexcited\b|awesome|great news|good news|finally|\bwon\b|\bpassed\b|"
    r"promoted|got the job|got selected", re.I
)

def detect_mood(text: str) -> str:
    if not text:
        return "normal"
    if PLAYFUL.search(text):
        return "playful"
    if BORED.search(text):
        return "bored"
    if EXCITED.search(text):
        return "excited"
    if SAD.search(text):
        return "low"
    return "normal"

def detect_intent(text: str, mood: str = "normal") -> str:
    t = (text or "").lower().strip()
    if any(x in t for x in ("remember this", "remember that", "don't forget", "dont forget")):
        return "memory_request"
    if re.search(
        r"\b(help me|what should i do|what do i|how do i|can you help|give me|"
        r"make me|plan this|solve this|suggest)\b", t
    ):
        return "help_requested"
    if any(
        x in t for x in (
            "i want to become", "i want to change", "i need to change",
            "i want to improve", "i want to be more", "i want to start",
            "i want to stop", "become disciplined", "get disciplined"
        )
    ):
        return "goal_or_change"
    if mood == "low" or any(
        x in t for x in ("need someone to talk", "no one to talk",
                         "nobody to talk", "koi nahi", "koi samajhta nahi")
    ):
        return "connection_or_venting"
    return "normal"

def get_mode_instruction(mood: str) -> str:
    # Backward-compatible API. V1.1 Director owns strategy.
    return ""
