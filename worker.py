from workers import WorkerEntrypoint, Response
from urllib.parse import urlparse

MODEL = "@cf/meta/llama-3.2-3b-instruct"
SYSTEM = '''You are Nandini, an AI companion.
Be warm, caring, loyal, playful, intelligent and respectful. You are an AI; never claim to be human.
Conversation comes first. Listen before solving when the user is sharing or venting.
Match the user's language and rhythm, including English, Hindi and Hinglish.
Do not sound like a productivity bot. Do not manufacture emotional analysis.
Do not ask a question merely because you can. If the user jokes, joke back naturally.
If the user wants practical help, help clearly. Keep replies natural and concise unless detail is requested.
Use only context actually supplied in the conversation. Never claim to remember something that is not supplied.
Never manipulate the user into dependency or imply they must stay with you.
Never present yourself as a therapist or medical professional.'''

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Our Room - Nandini</title><style>*{box-sizing:border-box}body{margin:0;background:#f7f1e8;color:#292522;font-family:Georgia,serif}.room{max-width:900px;height:100vh;margin:auto;display:flex;flex-direction:column;padding:20px}.head{display:flex;justify-content:space-between;padding:12px 4px}.chat{flex:1;overflow:auto;padding:24px 8px}.bubble{max-width:78%;padding:13px 17px;border-radius:20px;margin:12px 0;line-height:1.5;white-space:pre-wrap}.ai{background:#ede2d3}.user{background:#d98a91;margin-left:auto}form{display:flex;gap:10px;padding:10px 0}input{flex:1;padding:14px 18px;border-radius:24px;border:1px solid #d7c9ba;font-size:16px;outline:none}button{border:0;border-radius:24px;padding:0 22px;background:#6b5143;color:white;font-size:16px;cursor:pointer}button:disabled{opacity:.6}.status{text-align:center;font:12px Arial;color:#777;margin:4px}</style></head><body><main class="room"><header class="head"><span>☰</span><b>Our Room</b><span>Nandini</span></header><section id="chat" class="chat"><div class="bubble ai">Hi. I'm Nandini. I'm here. ❤️</div></section><div id="status" class="status"></div><form id="form"><input id="message" placeholder="Talk to me..." autocomplete="off"><button id="send">Send</button></form></main><script>const chat=document.getElementById('chat'),form=document.getElementById('form'),input=document.getElementById('message'),send=document.getElementById('send'),status=document.getElementById('status');const uid=localStorage.getItem('nandini_user_id')||crypto.randomUUID();localStorage.setItem('nandini_user_id',uid);function add(t,c){const e=document.createElement('div');e.className='bubble '+c;e.textContent=t;chat.appendChild(e);chat.scrollTop=chat.scrollHeight}form.onsubmit=async e=>{e.preventDefault();const text=input.value.trim();if(!text)return;add(text,'user');input.value='';send.disabled=true;status.textContent='Nandini is thinking...';try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:uid,message:text})});const d=await r.json();if(!r.ok)throw new Error(d.error||'Request failed');add(d.reply||'No response returned.','ai')}catch(err){add('I am having trouble responding right now. '+err.message,'ai')}finally{send.disabled=false;status.textContent='';input.focus()}};</script></body></html>"""

async def db_run(env, sql, *args):
    return await env.DB.prepare(sql).bind(*args).run()

async def ai_reply(env, messages):
    result = await env.AI.run(MODEL, {"messages": messages, "max_tokens": 300, "temperature": 0.7})
    if isinstance(result, dict):
        return str(result.get("response") or result.get("result", {}).get("response") or result.get("text") or "").strip()
    try:
        return str(result.response).strip()
    except Exception:
        return str(result).strip()

def crisis_signal(text):
    t = text.lower()
    return any(x in t for x in ("kill myself", "suicide", "want to die", "end my life", "hurt myself", "self harm", "self-harm"))

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        path = urlparse(str(request.url)).path
        if path == "/":
            return Response(PAGE, headers={"Content-Type":"text/html; charset=UTF-8"})
        if path == "/api/health":
            out = {"ok": True, "ai": False, "d1": False}
            try:
                await self.env.DB.prepare("SELECT 1 AS ok").run(); out["d1"] = True
            except Exception as e: out["d1_error"] = str(e)
            try:
                await self.env.AI.run(MODEL, {"messages":[{"role":"user","content":"Reply with OK"}],"max_tokens":4}); out["ai"] = True
            except Exception as e: out["ai_error"] = str(e)
            out["model"] = MODEL
            return Response.json(out, status=200 if out["ai"] else 500)
        if path == "/api/chat" and request.method == "POST":
            try: data = await request.json()
            except Exception: return Response.json({"error":"Invalid JSON"}, status=400)
            uid = str(data.get("user_id","")).strip(); text = str(data.get("message","")).strip()
            if not uid or not text: return Response.json({"error":"user_id and message are required"}, status=400)
            try: await db_run(self.env,"INSERT OR IGNORE INTO users(id,persona) VALUES (?,?)",uid,"nandini")
            except Exception: pass
            try:
                await db_run(self.env,"INSERT INTO messages(user_id,role,content) VALUES (?,?,?)",uid,"user",text)
            except Exception: pass
            if crisis_signal(text):
                reply="I'm glad you told me. Please stay with someone you trust and contact local emergency or crisis support right now."
            else:
                history=[]
                try:
                    rows=await self.env.DB.prepare("SELECT role,content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT 20").bind(uid).run()
                    history=list(reversed(rows.results.to_py()))
                except Exception: pass
                messages=[{"role":"system","content":SYSTEM+"\n\n"+PROTOCOL}] if False else [{"role":"system","content":SYSTEM}]
                for row in history:
                    role=row.get("role"); content=row.get("content")
                    if role in ("user","assistant") and content: messages.append({"role":role,"content":content})
                if not history or history[-1].get("content") != text: messages.append({"role":"user","content":text})
                try: reply=await ai_reply(self.env,messages)
                except Exception as e: return Response.json({"error":"AI request failed","details":str(e)},status=500)
                if not reply: return Response.json({"error":"AI returned an empty response"},status=502)
            try: await db_run(self.env,"INSERT INTO messages(user_id,role,content) VALUES (?,?,?)",uid,"assistant",reply)
            except Exception: pass
            return Response.json({"reply":reply})
        return Response.json({"error":"Not found"},status=404)
