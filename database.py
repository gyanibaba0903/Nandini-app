import os
from supabase import create_client, Client

# We get these from Render's environment variables later
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_message(user_id, role, content):
    """Saves a chat message to the cloud."""
    data = {"user_id": user_id, "role": role, "content": content}
    supabase.table("messages").insert(data).execute()

def load_history(user_id, limit=10):
    """Loads recent chat history from the cloud."""
    response = supabase.table("messages").select("role", "content").eq("user_id", user_id).order("id", desc=True).limit(limit).execute()
    # Reverse it so it's in chronological order
    return [{"role": r["role"], "content": r["content"]} for r in reversed(response.data)]
