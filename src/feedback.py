# feedback.py — remember which picks the reader liked / didn't, and use that to
# rewrite the interest prompt. Stored in feedback.json at the project root
# (gitignored), keyed by URL so it accumulates across runs.
import json
import os
import re

import ollama

import config

PATH = str(config.PROJECT_ROOT / "feedback.json")


def load():
    if os.path.exists(PATH):
        try:
            with open(PATH, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return []


def record(items):
    """items: [{url, title, summary, rating: 'keep'|'drop'}]. Upsert by url."""
    merged = {it["url"]: it for it in load()}
    for it in items:
        merged[it["url"]] = it
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(list(merged.values()), f, indent=2, ensure_ascii=False)


def clear():
    if os.path.exists(PATH):
        os.remove(PATH)


def refine_interest(current_prompt, items, limit=24):
    """Ask the local model for a new interest prompt given the rated items.
    Returns the new prompt string, or None if there's nothing usable."""
    rated = [it for it in items if it.get("rating") in ("keep", "drop")][-limit:]
    if not rated:
        return None
    lines = [f"[{it['rating'].upper()}] {it['title']} — {(it.get('summary') or '')[:200]}"
             for it in rated]
    user = (f"CURRENT INTEREST PROMPT:\n{current_prompt.strip()}\n\n"
            f"FEEDBACK:\n" + "\n".join(lines))
    resp = ollama.chat(
        model=config.MODEL_NAME,
        messages=[{"role": "system", "content": config.REFINE_PROMPT},
                  {"role": "user", "content": user}],
        options={"num_ctx": 8192},
    )
    out = resp["message"]["content"].strip()
    out = re.sub(r"^```[a-z]*\n?|\n?```$", "", out).strip().strip('"').strip()
    return out or None
