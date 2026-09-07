import os
from groq import Groq

class LLMAdapter:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"

    def generate_response(self, system_prompt, history, user_text):
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.72
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm having a little trouble thinking right now."

# Singleton instance
llm = LLMAdapter()
