# Nandini/Shiv V0.2 — Product/Engineering Spec

## North star
Build an AI companion that feels increasingly familiar with the individual:
remembering what the user chooses to share, understanding context, speaking
naturally, and knowing when to listen rather than solve.

## Core UX
- Our Room is the primary conversation space.
- Your Space is a personal life space, not an analytics/surveillance dashboard.
- Conversation is the hero.
- Warm, minimal, premium, soft and rounded.
- Voice mode will later minimize text and use a realistic avatar in the same room.
- Landing-page voice introduction comes before login/onboarding.

## Intelligence layers
Safety -> mood/intent/social signal -> conversation director -> persona/protocol/context
-> LLM -> post-generation -> memory/habits/relationship -> voice.

## Memory types planned
Working, episodic, semantic, relationship, procedural/routines,
derived communication preferences, temporary.

## Memory policy
Relevance, stability, importance, permission, sensitivity, confidence and
redundancy checks must be satisfied before long-term storage. Sensitive or
ambiguous information should not be silently stored.

## Communication DNA
Potential signals include language, response length, directness, warmth,
affection, humour, teasing, emoji use, question frequency, advice tolerance,
formality, preferred name, voice preference, speech speed, proactive tolerance
and topics to avoid. Inferred values need confidence and user override.

## Development rule
IDEA -> SPECIFICATION -> EXAMPLES -> ARCHITECTURE -> IMPLEMENTATION ->
AUTOMATED TESTS -> ACCEPTANCE -> NEXT FEATURE.
