# settings.py — the user's own interest prompt + source list, kept between app
# runs in my_settings.json at the project root (gitignored). config.py holds the
# shipped example; a saved file wins over it.
import json
import os

import config

PATH = str(config.PROJECT_ROOT / "my_settings.json")


def load():
    """{"interest": str, "sources": [{name, homepage, rss}]} — saved values where
    present, the config.py example otherwise."""
    data = {}
    if os.path.exists(PATH):
        try:
            with open(PATH, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}

    saved_sources = data.get("sources")
    return {
        "interest": data.get("interest") or config.INTEREST_PROMPT,
        "sources": saved_sources if isinstance(saved_sources, list)
        else [dict(s) for s in config.SOURCES],
        "exists": os.path.exists(PATH),
    }


def save(interest, sources):
    clean = [
        {"name": s.get("name", ""), "homepage": s.get("homepage", ""), "rss": s.get("rss")}
        for s in sources
    ]
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump({"interest": interest.strip(), "sources": clean}, f, indent=2, ensure_ascii=False)


def clear():
    if os.path.exists(PATH):
        os.remove(PATH)
