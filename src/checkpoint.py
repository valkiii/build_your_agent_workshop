# checkpoint.py — save / load the approved articles from a curation run.
#
# The slow part of a run is discovery + the LLM (summarize, judge, quiz). Once
# that's done, the "Act" steps (EPUB, podcast) are fast and repeatable. Saving a
# checkpoint lets you run them later — or on a different machine — without
# repeating the pipeline. Handy for demos: curate once, then act on it as a
# separate step.
import json
import os
from datetime import date

import config


def default_path():
    return os.path.join(config.OUTPUT_DIR, f"Curated News of {date.today().isoformat()}.json")


def save(approved, path=None):
    """Write the list of approved-article dicts to JSON. Returns the path."""
    path = path or default_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(approved, f, indent=2, ensure_ascii=False)
    return path


def load(src):
    """Load a saved run. `src` is a path or an already-open file object."""
    data = json.load(src) if hasattr(src, "read") else _load_path(src)
    if not isinstance(data, list) or (data and not isinstance(data[0], dict)):
        raise ValueError("This file doesn't look like a saved run (expected a JSON list of articles).")
    return data


def _load_path(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def saved_runs():
    """Paths of checkpoint JSONs in OUTPUT_DIR, newest first."""
    if not os.path.isdir(config.OUTPUT_DIR):
        return []
    files = [os.path.join(config.OUTPUT_DIR, n)
             for n in os.listdir(config.OUTPUT_DIR) if n.lower().endswith(".json")]
    return sorted(files, key=os.path.getmtime, reverse=True)
