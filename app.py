import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from crisis_intercept import check_crisis, get_crisis_response, log_crisis_event
from mood_detector import detect_mood, detect_intent
from conversation_director import build_director_context
from database import (
    init_db, ensure_user, get_user, save_message, load_history,
    add_memory, list_memories,
)
from memory_engine import candidate_from_user_text

BASE = Path(__file__).resolve().parent
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
API_KEY = os.environ.get("GROQ_API_KEY")
client = None

app = Flask(__name__, template_folder="templates", static_folder="static")
init_db()

def persona_prompt(persona):
    filename = "system_prompt_shiv.txt" if persona == "shiv" else "system_prompt_nandini.txt"
    return (BASE / filename).read_text(encoding="utf-8")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "llm_configured": bool(client), "model": MODEL})

@app.post("/api/onboarding")
def onboarding():
    data = request.get_json(force=True) or {}
    user_id = (data.get("user_id") or uuid.uuid4().hex[:12]).strip()
    age_confirmed = bool(data.get("age_confirmed"))
    if not age_confirmed:
        return jsonify({"error": "This V0.2 prototype is for adults 18+ only."}), 403
    persona = data.get("persona", "nandini")
    if persona not in {"nandini", "shiv"}:
        persona = "nandini"
    ensure_user(
        user_id,
        name=(data.get("name") or "Friend").strip(),
        persona=persona,
        profile_type=(data.get("profile_type") or "other").strip().lower(),
        age_confirmed=True,
    )
    return jsonify({"ok": True, "user_id": user_id})

@app.post("/api/chat")
def chat():
    data = request.get_json(force=True) or {}
    user_id = (data.get("user_id") or "").strip()
    user_text = (data.get("message") or "").strip()
    persona = data.get("persona", "nandini")
    if not user_id or not user_text:
        return jsonify({"error": "user_id and message are required"}), 400

    user = get_user(user_id)
    if not user:
        ensure_user(user_id, persona=persona, age_confirmed=True)
        user = get_user(user_id)

    if check_crisis(user_text):
        log_crisis_event(user_id)
        response = get_crisis_response()
        save_message(user_id, "user", user_text)
        save_message(user_id, "assistant", response)
        return jsonify({"reply": response, "safety": True})

    mood = detect_mood(user_text)
    intent = detect_intent(user_text, mood)
    director = build_director_context(user_id, user_text, mood, persona)
    protocol = (BASE / "conversation_protocol.txt").read_text(encoding="utf-8")
    prompt = persona_prompt(persona) + "\n\n" + protocol + director
    memories = list_memories(user_id, 20)
    if memories:
        relevant = "\n".join(f"- {m['content']}" for m in memories[:10])
        prompt += "\n\n[RELEVANT USER CONTEXT]\n" + relevant

    history = load_history(user_id, 30)
    messages = [{"role": "system", "content": prompt}] + history + [{"role": "user", "content": user_text}]

    if not client:
        response = (
            "I’m connected to the conversation engine, but the LLM key isn’t configured yet. "
            "The safety, mood, intent, director and memory layers are running."
        )
    else:
        result = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.72,
        )
        response = result.choices[0].message.content.strip()

    save_message(user_id, "user", user_text)
    save_message(user_id, "assistant", response)

    candidate = candidate_from_user_text(user_text)
    if candidate and intent == "memory_request":
        add_memory(
            user_id, candidate["type"], candidate["content"],
            confidence=candidate["confidence"], confirmed=True
        )

    return jsonify({
        "reply": response,
        "mood": mood,
        "intent": intent,
        "strategy": director.split("strategy=", 1)[1].split("\n", 1)[0],
        "safety": False,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
