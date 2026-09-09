import json, os
from config import STATE_FILE

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"seen_urls": []}
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
