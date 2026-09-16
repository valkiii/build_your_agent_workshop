# diagnostics.py — turns a discovery run's per-source trace into a plain-text
# report a participant can download and send to the facilitator (and the
# facilitator can read without needing to reproduce the problem themselves).
# No Streamlit here on purpose — main.py's CLI track can use this too.
import os
from datetime import datetime

import config


def format_report(interest_prompt, source_diagnostics, curation=None):
    """interest_prompt: str. source_diagnostics: the list discover_new_articles()
    returns. curation: optional {"checked": int, "approved": int, "sample_rejections":
    [{"title": str, "reason": str}, ...]} from a full run (discovery-only runs omit it).
    Returns the report as one string."""
    lines = []
    w = lines.append
    w("=" * 70)
    w("Content Curator — diagnostic report")
    w("=" * 70)
    w(f"Generated:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    w(f"Model:         {config.MODEL_NAME}")
    w(f"Days lookback: {config.DAYS_LOOKBACK}")
    w("Interest prompt:")
    for line in interest_prompt.strip().splitlines():
        w(f"  {line}")
    w("")
    w("-" * 70)
    w(f"Sources checked: {len(source_diagnostics)}")
    w("-" * 70)
    for i, d in enumerate(source_diagnostics, 1):
        w(f"[{i}] {d['name']}")
        w(f"    Homepage: {d['homepage'] or '(none)'}")
        w(f"    RSS:      {d['rss'] or '(none configured)'}")
        w(f"    Method:   {d['method']}")
        if d.get("detail"):
            w(f"              {d['detail']}")
        if d.get("error"):
            w(f"    ERROR:    {d['error']}")
        w(f"    Entries found (raw):       {d['raw_entries']}")
        w(f"    ...after date-range filter: {d['after_date_filter']}")
        w(f"    ...after 'already seen' filter: {d['after_seen_filter']}")
        w("")

    total_new = sum(d["after_seen_filter"] for d in source_diagnostics)
    w("-" * 70)
    w(f"TOTAL new articles found across all sources: {total_new}")
    if total_new == 0:
        w("")
        w("Nothing to check this run — look at the per-source detail above:")
        w("  - 'homepage fallback' + no RSS  -> that source has no RSS feed")
        w("    configured; add one under 'RSS feed URL' if the site has one.")
        w("  - a 4xx/5xx homepage status     -> that site is blocking automated")
        w("    requests; no fix from this app, try a different source.")
        w("  - entries found but 0 after the seen-filter -> every article this")
        w("    source currently has was already checked in a previous run —")
        w("    try '🔄 Forget seen articles', or it just has nothing new today.")
    w("-" * 70)

    if curation is not None:
        w("")
        w("-" * 70)
        w("Curation (after discovery)")
        w("-" * 70)
        w(f"Articles checked:  {curation['checked']}")
        w(f"Articles approved: {curation['approved']}")
        if curation["checked"] and not curation["approved"]:
            w("")
            w("Discovery found articles but the model approved none of them.")
            w("Sample rejections (reason the model gave):")
            for r in curation.get("sample_rejections", [])[:5]:
                w(f"  - \"{r['title']}\" — {r['reason']}")
            w("")
            w("If every article is being rejected, the interest prompt is likely")
            w("too narrow for what these sources actually publish — try loosening")
            w("it, or picking sources closer to the stated interest.")
        w("-" * 70)

    w("")
    w("=" * 70)
    return "\n".join(lines)


def save_report(text):
    """Writes the report to logs/<timestamp>.txt (gitignored, created on first
    use) and returns the path. Never raises — a logging failure shouldn't be
    the reason a participant's run breaks."""
    try:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        path = os.path.join(config.LOGS_DIR, datetime.now().strftime("run-%Y%m%d-%H%M%S.txt"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path
    except OSError:
        return None
