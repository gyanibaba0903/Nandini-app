from flask import Flask, request, jsonify, render_template
from database import save_message, load_history
from llm_adapter import llm
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(force=True) or {}
    user_text = (data.get("message") or "").strip()
    user_id = "default_user"

    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    # 1. Load past conversation history from Supabase
    history = load_history(user_id, limit=10)

    # 2. Save the user's new message to Supabase
    save_message(user_id, "user", user_text)

    # 3. Ask the LLM for a response
    system_prompt = "You are Nandini, a warm, witty, and caring AI companion. You speak naturally and use Hinglish when the user does. Keep replies to 1-3 sentences. Do not give lists or unsolicited advice."

    reply = llm.generate_response(system_prompt, history, user_text)

    # 4. Save Nandini's reply to Supabase
    save_message(user_id, "assistant", reply)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
