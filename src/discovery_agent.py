# discovery_agent.py — Perceive step.
# RSS-first; falls back to scraping the homepage for post links only when no
# working feed exists. Relative URLs are resolved to absolute (this was a real
# bug once — don't regress it).
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

import config
from state import load_state, save_state


def try_rss(source):
    """Return a list of article dicts from the source's RSS feed, or None if it
    has no usable feed (so the caller can fall back to homepage scraping)."""
    if not source.get("rss"):
        return None
    feed = feedparser.parse(source["rss"])
    if not feed.entries:  # tolerate feed.bozo — many valid feeds set it over trivia
        return None
    return [
        {
            "url": e.link,
            "title": e.title,
            "source": source["name"],
            "published": datetime(*e.published_parsed[:6])
            if getattr(e, "published_parsed", None)
            else None,
        }
        for e in feed.entries
    ]


def looks_like_real_post(url):
    """Filter out nav/category links (".../blog/", ".../category/ai"). Real posts
    have a slug: hyphenated and reasonably long."""
    slug = url.rstrip("/").split("/")[-1]
    return "-" in slug and len(slug) > 10


def fallback_homepage_scrape(source):
    """Returns (results, status_note) — status_note is a short human-readable
    string ("HTTP 200", "HTTP 403", "connection failed (Timeout)", ...) so the
    caller can report exactly what happened, not just how many articles came
    back. See discover_new_articles()'s per-source diagnostics."""
    try:
        resp = requests.get(
            source["homepage"], headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
    except requests.RequestException as e:
        return [], f"connection failed ({type(e).__name__})"
    status_note = f"HTTP {resp.status_code}"
    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.select("a[href*='/blog/'], a[href*='/post/']")
    seen_urls, results = set(), []
    for a in links:
        href = a.get("href")
        if not href:
            continue
        full_url = urljoin(source["homepage"], href)  # resolve relative paths to absolute
        if full_url in seen_urls or not looks_like_real_post(full_url):
            continue
        seen_urls.add(full_url)
        results.append(
            {
                "url": full_url,
                "title": a.get_text(strip=True) or full_url,
                "source": source["name"],
                "published": None,
            }
        )
    return results[:10], status_note


def discover_new_articles():
    # Read config attributes live (not `from config import ...`) so the Streamlit
    # app's in-session edits to SOURCES take effect.
    state = load_state()
    seen = set(state["seen_urls"])
    cutoff = datetime.now() - timedelta(days=config.DAYS_LOOKBACK)

    new_articles = []
    diagnostics = []  # one dict per source — see diagnostics.py for the report built from this
    for source in config.SOURCES:
        diag = {
            "name": source.get("name") or "(unnamed source)",
            "homepage": source.get("homepage", ""),
            "rss": source.get("rss") or None,
            "method": None,
            "detail": None,
            "error": None,
            "raw_entries": 0,
            "after_date_filter": 0,
            "after_seen_filter": 0,
        }
        try:
            entries = try_rss(source)
            if entries is None:
                diag["method"] = "homepage fallback"
                diag["detail"] = (
                    "no RSS feed configured for this source"
                    if not source.get("rss")
                    else "RSS feed configured but returned no entries"
                )
                print(f"  [{source['name']}] no working RSS feed, falling back to homepage scrape")
                entries, status_note = fallback_homepage_scrape(source)
                diag["detail"] += f"; homepage fetch: {status_note}"
            else:
                diag["method"] = "rss"
        except Exception as e:
            diag["method"] = "error"
            diag["error"] = f"{type(e).__name__}: {e}"
            entries = []

        diag["raw_entries"] = len(entries)

        after_date = [e for e in entries if not (e["published"] and e["published"] < cutoff)]
        diag["after_date_filter"] = len(after_date)

        after_seen = [e for e in after_date if e["url"] not in seen]
        diag["after_seen_filter"] = len(after_seen)

        new_articles.extend(after_seen)
        diagnostics.append(diag)

    return new_articles, state, diagnostics


def mark_as_seen(articles, state):
    # Rejected articles are marked seen too, so re-runs don't re-summarize them forever.
    state["seen_urls"].extend(a["url"] for a in articles)
    save_state(state)
