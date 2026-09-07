import os
from openai import OpenAI

class LLMAdapter:
    def __init__(self):
        # Using OpenAI SDK to talk to Groq to bypass Python 3.14 httpx bug
        self.client = OpenAI(
            api_key=os.environ.get("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.1-8b-instant"

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

llm = LLMAdapter()
