# assistant.py — a small chat helper that talks a new user through writing their
# interest prompt and picking blog sources, using the same local model.
import re

import ollama

import config


def reply_stream(history):
    """history: list of {"role": "user"|"assistant", "content": str}.
    Yields the assistant's next message in chunks (for st.write_stream)."""
    messages = [{"role": "system", "content": config.ASSISTANT_PROMPT}] + history
    for chunk in ollama.chat(model=config.MODEL_NAME, messages=messages,
                             stream=True, options={"num_ctx": 8192}):
        yield chunk["message"]["content"]


def extract(text):
    """Pull an <interest>…</interest> paragraph and <sources> lines out of an
    assistant message. Returns (interest_or_None, [ {name, homepage, rss} ])."""
    interest = None
    m = re.search(r"<interest>(.*?)</interest>", text, re.S | re.I)
    if m and m.group(1).strip():
        interest = m.group(1).strip()

    sources = []
    m = re.search(r"<sources>(.*?)</sources>", text, re.S | re.I)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip().lstrip("-*• ").strip()
            if "|" not in line:
                continue
            name, url = (p.strip() for p in line.split("|", 1))
            if name:
                sources.append({"name": name, "homepage": url, "rss": None})
    return interest, sources
