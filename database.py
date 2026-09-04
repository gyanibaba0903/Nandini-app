"""
SQLite development persistence.
Production should use Supabase/PostgreSQL.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "nandini_shiv.db"

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            user_id TEXT PRIMARY KEY,
            name TEXT,
            persona TEXT,
            profile_type TEXT,
            age_confirmed INTEGER DEFAULT 0,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, role TEXT, content TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS memories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, type TEXT, content TEXT, confidence REAL,
            user_confirmed INTEGER DEFAULT 0, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS habits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, content TEXT, created_at TEXT
        );
        """)

def ensure_user(user_id, name="Friend", persona="nandini",
                age_confirmed=True, profile_type="other"):
    with _conn() as c:
        c.execute(
            """INSERT INTO users(user_id,name,persona,profile_type,age_confirmed,created_at)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(user_id) DO UPDATE SET
               name=excluded.name, persona=excluded.persona,
               profile_type=excluded.profile_type, age_confirmed=excluded.age_confirmed""",
            (user_id, name, persona, profile_type, int(age_confirmed),
             datetime.now(timezone.utc).isoformat()),
        )

def get_user(user_id):
    with _conn() as c:
        r = c.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(r) if r else None

def save_message(user_id, role, content):
    with _conn() as c:
        c.execute(
            "INSERT INTO messages(user_id,role,content,created_at) VALUES(?,?,?,?)",
            (user_id, role, content, datetime.now(timezone.utc).isoformat()),
        )

def load_history(user_id, limit=30):
    with _conn() as c:
        rows = c.execute(
            "SELECT role,content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    rows = list(reversed(rows))
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def add_memory(user_id, kind, content, confidence=0.85, confirmed=False):
    with _conn() as c:
        c.execute(
            """INSERT INTO memories(user_id,type,content,confidence,user_confirmed,created_at)
               VALUES(?,?,?,?,?,?)""",
            (user_id, kind, content, confidence, int(confirmed),
             datetime.now(timezone.utc).isoformat()),
        )

def list_memories(user_id, limit=50):
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM memories WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]
