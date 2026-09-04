def make_monthly_insight(memories=None, habits=None):
    memories = memories or []
    habits = habits or []
    if not memories and not habits:
        return "I've learned a few things about you this month — we're just getting started."
    return (
        "I've learned a few things about you this month. "
        "There are some patterns worth noticing, and we can keep the reflection "
        "light and useful."
    )
