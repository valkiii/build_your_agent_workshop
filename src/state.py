# state.py — tiny JSON file that remembers which article URLs we've already
# processed, so re-runs don't re-evaluate them (rejects included).
import json, os

from config import STATE_FILE


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"seen_urls": []}
    with open(STATE_FILE) as f:
        data = json.load(f)
    data.setdefault("seen_urls", [])
    return data


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def reset_seen():
    """Forget every previously-seen URL so the next run re-checks everything.
    Handy for demos: tweak the interest prompt, reset, run again, and watch the
    approve/reject decisions change on the same set of articles."""
    save_state({"seen_urls": []})
