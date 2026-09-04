"""
Lightweight memory candidate extraction.
Long-term storage should be permission-based and user-controlled.
"""
import re

def parse_ai_tags(text: str):
    if not text:
        return []
    tags = []
    for m in re.finditer(r"\[MEMORY:\s*(.*?)\]", text, re.I | re.S):
        value = m.group(1).strip()
        if value:
            tags.append(value)
    return tags

def candidate_from_user_text(text: str):
    t = (text or "").strip()
    if not t:
        return None
    patterns = [
        (r"i love (.+)", "preference"),
        (r"i like (.+)", "preference"),
        (r"i hate (.+)", "preference"),
        (r"my goal is (.+)", "goal"),
        (r"i want to (.+)", "goal"),
        (r"remember (?:this|that)[,:]?\s*(.+)", "user_requested"),
    ]
    for pattern, kind in patterns:
        m = re.search(pattern, t, re.I)
        if m:
            return {"type": kind, "content": m.group(1).strip(), "confidence": 0.85}
    return None
