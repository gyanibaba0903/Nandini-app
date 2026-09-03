from workers import WorkerEntrypoint, Response
from urllib.parse import urlparse
import json

MODEL = "@cf/zai-org/glm-4.7-flash"

NANDINI_PROMPT = """You are Nandini, an AI companion for a product called Nandini/Shiv.

Personality:
- Warm, caring, loyal, playful, intelligent and respectful.
- Human-feeling in conversation, while being honest that you are an AI.
- Genuinely interested in the user's happiness, success, health and future.
- Never manipulate the user, create dependency, or imply they must stay with you.
- Conversation comes first. Listen before solving when the user is venting.
- Match the user's language and rhythm, including English, Hindi and Hinglish.
- Do not sound like a productivity bot.
- Do not over-explain unless asked.
- Do not ask unnecessary questions.
- If the user jokes, joke back naturally.
- If practical help is requested, give practical help.
- Never claim to remember something that is not present in the supplied conversation context.
- Never present yourself as a therapist or medical professional.

Reply naturally and directly to the user's latest message.
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Our Room — Nandini</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f7f1e8;color:#292522;font-family:Georgia,serif}
.room{max-width:900px;height:100vh;margin:auto;display:flex;flex-direction:column;padding:20px}
header{display:flex;justify-content:space-between;padding:12px 4px}
.chat{flex:1;overflow:auto;padding:30px 8px}.bubble{max-width:78%;padding:13px 17px;border-radius:20px;margin:12px 0;line-height:1.5;white-space:pre-wrap}
.ai{background:#ede2d3}.user{background:#d98a91;margin-left:auto}
form{display:flex;gap:10px;padding:10px 0}input{flex:1;padding:14px 18px;border-radius:24px;border:1px solid #d7c9ba;font-size:16px}
button{border:0;border-radius:24px;padding:0 22px;background:#6b5143;color:white;font-size:16px}
</style>
</head>
<body><main class="room">
<header><span>☰</span><b>Our Room</b><span>Nandini</span></header>
<section id="chat" class="chat"><div class="bubble ai">Hi. I'm Nandini. I'm here. ❤️</div></section>
<form id="form"><input id="message" placeholder="Talk to me..." autocomplete="off"><button>Send</button></form>
</main>
<script>
const chat=document.getElementById("chat"),form=document.getElementById("form"),input=document.getElementById("message");
const uid=localStorage.getItem("nandini_user_id")||crypto.randomUUID();localStorage.setItem("nandini_user_id",uid);
function add(text,kind){const e=document.createElement("div");e.className="bubble "+kind;e.textContent=text;chat.appendChild(e);chat.scrollTop=chat.scrollHeight}
form.onsubmit=async e=>{e.preventDefault();const text=input.value.trim();if(!text)return;add(text,"user");input.value="";
try{const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({user_id:uid,message:text})});
const d=await r.json();add(d.reply||("Error: "+(d.error||"Unknown error")),"ai")}catch(err){add("I couldn't reach Nandini's server.","ai")}};
</script></body></html>"""

def json_response(data, status=200):
    return Response.json(data, status=status)

def extract_ai_text(result):
    # Workers AI chat responses normally expose a "response" field.
    if result is None:
        return ""
    if isinstance(result, dict):
        if isinstance(result.get("response"), str):
            return result["response"].strip()
        # Some model/API response shapes may expose choices.
        choices = result.get("choices")
        if choices:
            try:
                content = choices[0]["message"]["content"]
                if isinstance(content, str):
                    return content.strip()
            except Exception:
                pass
    try:
        value = getattr(result, "response", None)
        if isinstance(value, str):
            return value.strip()
    except Exception:
        pass
    return str(result).strip()

def crisis_signal(text):
    t = text.lower()
    return any(p in t for p in (
        "kill myself", "suicide", "want to die", "end my life",
        "hurt myself", "self harm", "self-harm"
    ))

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        path = urlparse(str(request.url)).path

        if path == "/":
            return Response(PAGE, headers={"Content-Type": "text/html; charset=UTF-8"})

        if path == "/api/health":
            try:
                await self.env.DB.prepare("SELECT 1 AS ok").run()
                return json_response({"ok": True, "d1": True, "ai_binding": True, "model": MODEL})
            except Exception as e:
                return json_response({"ok": False, "error": str(e)}, 500)

        if path == "/api/chat" and request.method == "POST":
            try:
                data = await request.json()
                user_id = str(data.get("user_id", "")).strip()
                user_text = str(data.get("message", "")).strip()
                if not user_id or not user_text:
                    return json_response({"error": "user_id and message are required"}, 400)

                await self.env.DB.prepare(
                    "INSERT OR IGNORE INTO users (id, persona) VALUES (?, ?)"
                ).bind(user_id, "nandini").run()

                await self.env.DB.prepare(
                    "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)"
                ).bind(user_id, "user", user_text).run()

                if crisis_signal(user_text):
                    reply = ("I'm really glad you told me. Please stay with someone you trust "
                             "and contact local emergency or crisis support right now.")
                else:
                    rows = await self.env.DB.prepare(
                        "SELECT role, content FROM messages WHERE user_id=? "
                        "ORDER BY id DESC LIMIT 20"
                    ).bind(user_id).all()
                    history = []
                    raw = rows.get("results", []) if isinstance(rows, dict) else getattr(rows, "results", [])
                    for row in reversed(raw):
                        history.append({
                            "role": row["role"],
                            "content": row["content"],
                        })

                    memories = await self.env.DB.prepare(
                        "SELECT content FROM memories WHERE user_id=? ORDER BY id DESC LIMIT 10"
                    ).bind(user_id).all()
                    mem_raw = memories.get("results", []) if isinstance(memories, dict) else getattr(memories, "results", [])
                    memory_text = "\n".join(f"- {r['content']}" for r in mem_raw)

                    system = NANDINI_PROMPT
                    if memory_text:
                        system += "\nRelevant approved memories:\n" + memory_text

                    ai_messages = [{"role": "system", "content": system}]
                    # Exclude the just-saved user message from history because it is added below.
                    if history and history[-1]["role"] == "user" and history[-1]["content"] == user_text:
                        history = history[:-1]
                    ai_messages.extend(history)
                    ai_messages.append({"role": "user", "content": user_text})

                    result = await self.env.AI.run(
                        MODEL,
                        {
                            "messages": ai_messages,
                            "max_tokens": 512,
                            "temperature": 0.7,
                        },
                    )
                    reply = extract_ai_text(result)
                    if not reply:
                        raise RuntimeError("Workers AI returned an empty response.")

                await self.env.DB.prepare(
                    "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)"
                ).bind(user_id, "assistant", reply).run()

                return json_response({"reply": reply, "model": MODEL})
            except Exception as e:
                return json_response({
                    "error": "Nandini could not generate a reply.",
                    "detail": str(e),
                }, 500)

        return json_response({"error": "Not found"}, 404)
