import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL", "").strip()
key: str = os.environ.get("SUPABASE_KEY", "").strip()

# ULTIMATE FIX: Force the URL to be perfectly clean. No trailing slashes, no paths.
if ".supabase.co" in url:
    url = url.split(".supabase.co")[0] + ".supabase.co"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"!!! SUPABASE INIT ERROR: {e} !!!")
    supabase = None

def save_message(user_id, role, content):
    if not supabase: return
    try:
        data = {"user_id": user_id, "role": role, "content": content}
        supabase.table("messages").insert(data).execute()
    except Exception as e:
        print(f"!!! DB SAVE ERROR: {e} !!!")

def load_history(user_id, limit=10):
    if not supabase: return []
    try:
        response = supabase.table("messages").select("role", "content").eq("user_id", user_id).order("id", desc=True).limit(limit).execute()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(response.data)]
    except Exception as e:
        print(f"!!! DB LOAD ERROR: {e} !!!")
        return []
