# assistant.py — a small chat helper that talks a new user through writing their
# interest prompt and picking blog sources, using the same local model.
import re

import ollama
import requests

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


def verify_sources(sources, timeout=4):
    """A small local model asked to name real websites will sometimes invent a
    plausible-sounding one that doesn't exist (confirmed live: it suggested
    "ricettedelchef.it", which has no DNS record at all). The prompt now asks
    it not to, but that's a request, not a guarantee — this is the actual
    backstop, since it's cheap to just check.

    Any response at all — even an error status like 401/403 — proves the
    domain is real and just wasn't picked up on: a request-level failure
    (DNS doesn't resolve, connection refused, timeout) is the specific signal
    that it was invented. Returns (verified, dropped) — two lists of source
    dicts, same shape as the input.
    """
    verified, dropped = [], []
    for s in sources:
        url = s.get("homepage", "")
        if not url:
            dropped.append(s)
            continue
        try:
            requests.head(url, timeout=timeout, allow_redirects=True,
                          headers={"User-Agent": "Mozilla/5.0"})
            verified.append(s)
        except requests.exceptions.RequestException:
            dropped.append(s)
    return verified, dropped
