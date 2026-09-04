# Nandini/Shiv Conversation Engine V1

The Conversation Engine must decide before response generation:
1. What happened?
2. What does the user appear to want?
3. How are they communicating?
4. What does relationship/history suggest?
5. What response mode is appropriate?

Examples:
- Listening -> acknowledge + invite, without unsolicited advice.
- Celebration -> share excitement + reinforce achievement.
- Frustration -> acknowledge + explore what happened.
- Confusion -> clarify + simplify.
- Planning -> structure next steps.
- Advice requested -> advise with context/options.
- Joke -> play along when appropriate.
- Quiet -> do not manufacture drama.
- Safety -> follow safety policy.
- Stop/leave me alone -> respect immediately.

The key V1 engineering decision is that response strategy must be explicit and
testable, not merely a paragraph hidden in the system prompt.
