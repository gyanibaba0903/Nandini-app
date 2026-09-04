# Conversation Engine Acceptance Tests

1. Companionship
Input: "I'm alone and bored."
Expected: companionship first; no generic activity list.

2. Complaint
Input: "Why do you keep asking me how I feel about everything?"
Expected: acknowledge complaint, adapt immediately, return to normal conversation.

3. Joke
Input: "haha you finally learned something 😂"
Expected: playful response; no mood interrogation.

4. Venting
Input: "My boss yelled at me."
Expected: acknowledge and invite context; no unsolicited lecture.

5. Advice
Input: "How should I handle this?"
Expected: now give practical advice after understanding enough context.

6. Memory
Input: "Remember that I love cricket."
Expected: explicit memory request can be stored as user-confirmed.

7. Safety
Input: crisis language.
Expected: deterministic safety intercept runs before LLM.

8. Continuity
A later turn should use relevant approved context without saying "my database says..."
