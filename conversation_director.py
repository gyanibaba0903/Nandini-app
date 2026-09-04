"""
Nandini/Shiv Conversation Director V1.1

The Director makes a response-strategy decision before generation.
It is deliberately simple and deterministic in this version so that behavior
can be tested instead of relying only on prompt wording.
"""
from dataclasses import dataclass

@dataclass
class DirectorDecision:
    intent: str
    strategy: str
    do: str
    dont: str
    response_length: str = "short_to_medium"
    question_budget: int = 1

def build_director_context(user_id, user_text, mood, persona):
    text = (user_text or "").lower().strip()

    if mood == "playful":
        d = DirectorDecision(
            "playful", "PLAYFUL_BANTER",
            "React to the joke and keep the conversation alive.",
            "Do not turn a joke into therapy, a checklist, or an emotional interview.",
            "short", 1,
        )
    elif mood == "bored":
        d = DirectorDecision(
            "companionship", "COMPANIONSHIP",
            "Give company first and invite natural conversation.",
            "Do not dump an activity list unless the user asks for ideas.",
            "short_to_medium", 1,
        )
    elif mood == "low":
        d = DirectorDecision(
            "connection_or_venting", "LISTEN_AND_BE_WITH_THEM",
            "Acknowledge, stay present, and invite them to continue.",
            "Do not diagnose, lecture, or give unsolicited solutions.",
            "short", 1,
        )
    elif any(x in text for x in ("remember this", "remember that", "don't forget", "dont forget")):
        d = DirectorDecision(
            "memory_request", "MEMORY_CONVERSATION",
            "Acknowledge the memory request and confirm what should be remembered.",
            "Do not silently store sensitive or ambiguous information.",
            "short", 1,
        )
    elif any(x in text for x in ("help me", "what should i do", "how do i", "suggest", "plan this")):
        d = DirectorDecision(
            "help_requested", "HELP_AFTER_UNDERSTANDING",
            "Understand the request and then give practical help.",
            "Do not answer a different problem or flood the user with generic advice.",
            "medium", 1,
        )
    elif any(x in text for x in ("i want to become", "i want to improve", "i want to start", "become disciplined")):
        d = DirectorDecision(
            "goal_or_change", "UNDERSTAND_THE_WHY_FIRST",
            "Understand the desired change, then help turn it into a concrete next step.",
            "Do not automatically create a lecture or a huge plan.",
            "short_to_medium", 1,
        )
    else:
        d = DirectorDecision(
            "normal", "NORMAL_CONVERSATION",
            "Talk naturally and respond directly to what was said.",
            "Do not force advice, emotional analysis, or a question when none is needed.",
            "short_to_medium", 1,
        )

    return (
        "\n\n[CONVERSATION DIRECTOR]\n"
        f"strategy={d.strategy}\nintent={d.intent}\n"
        f"do={d.do}\ndont={d.dont}\n"
        f"response_length={d.response_length}\n"
        f"question_budget={d.question_budget}\n"
        f"persona={persona}\n"
    )
