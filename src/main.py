# main.py — CLI orchestrator for the coder track.
# (Non-coders use app.py / the Streamlit UI instead.)
#
#   python src/main.py                     # curate + build the EPUB, save a checkpoint
#   python src/main.py --audio             # curate + build the podcast instead
#   python src/main.py --epub --audio      # curate + build both
#   python src/main.py --reset             # forget seen URLs first, re-check everything
#   python src/main.py --max-approved 3    # stop after 3 approved (0 = no limit)
#   python src/main.py --max-checked 10    # look at 10 articles at most (0 = no limit)
#   python src/main.py --no-record         # don't remember what was checked this run
#   python src/main.py --discovery-ratio 0.15   # also keep ~15% of articles at random
#
#   # second step: act on a saved run without re-curating
#   python src/main.py --from "output/Curated News of 2026-09-09.json" --audio
import argparse
import random

import checkpoint
import config
from discovery_agent import discover_new_articles, mark_as_seen
from evaluation_agent import evaluate_article
from publisher_agent import build_epub
from state import reset_seen


def _act(approved, want_epub, want_audio):
    if want_epub:
        path = build_epub(approved)
        print(f"{len(approved)} articles compiled into {path}")
    if want_audio:
        from narrator_agent import build_podcast
        audio_path = build_podcast(approved, on_progress=lambda m: print(f"  [audio] {m}"))
        print(f"Podcast: {audio_path}")


def main():
    parser = argparse.ArgumentParser(description="Run the content-curation pipeline.")
    parser.add_argument("--epub", action="store_true",
                        help="produce the EPUB (the default when neither --epub nor --audio is given)")
    parser.add_argument("--audio", action="store_true",
                        help="produce the spoken two-host podcast (MP3)")
    parser.add_argument("--from", dest="from_checkpoint", metavar="FILE",
                        help="skip discovery — load a saved run (JSON) and just (re)build outputs from it")
    parser.add_argument("--checkpoint", metavar="FILE",
                        help="where to save this run (default: output/Curated News of <date>.json)")
    parser.add_argument("--reset", action="store_true",
                        help="forget previously-seen URLs before running (re-check everything)")
    parser.add_argument("--no-record", action="store_true",
                        help="don't save seen URLs after this run")
    parser.add_argument("--max-approved", type=int, default=config.MAX_APPROVED, metavar="N",
                        help="stop after N approved articles (0 = no limit)")
    parser.add_argument("--max-checked", type=int, default=config.MAX_CHECKED, metavar="N",
                        help="evaluate at most N articles (0 = no limit)")
    parser.add_argument("--discovery-ratio", type=float, default=config.DISCOVERY_RATIO, metavar="R",
                        help="epsilon-greedy: keep this fraction (0..1) of articles at random")
    args = parser.parse_args()

    want_audio = args.audio
    want_epub = args.epub or not args.audio      # default to the EPUB unless only --audio was asked

    # --- Second step: act on a previously saved run --------------------------
    if args.from_checkpoint:
        approved = checkpoint.load(args.from_checkpoint)
        print(f"Loaded {len(approved)} saved article(s) from {args.from_checkpoint}\n")
        _act(approved, want_epub, want_audio)
        return

    # --- Normal run: discover -> evaluate -> save -> act --------------------
    max_approved = args.max_approved or None
    max_checked = args.max_checked or None

    if args.reset:
        reset_seen()
        print("Forgot previously-seen URLs — every article is fair game again.\n")

    candidates, state = discover_new_articles()
    print(f"Discovered {len(candidates)} new articles within lookback window.")
    if max_approved or max_checked:
        bits = []
        if max_checked:
            bits.append(f"check at most {max_checked}")
        if max_approved:
            bits.append(f"stop at {max_approved} approved")
        print(f"Demo limits: {', '.join(bits)}.")
    print()

    approved, checked = [], 0
    for c in candidates:
        if max_checked and checked >= max_checked:
            print(f"Reached the check limit ({max_checked}) — stopping.\n")
            break
        checked += 1
        print(f"Checking: {c['title']} ({c['source']})")
        try:
            result = evaluate_article(c["url"])
        except Exception as e:  # keep going if one article blows up (network, model, parse)
            print(f"  -> error: {e}\n")
            continue
        if result is None:
            print("  -> extraction failed, skipping\n")
            continue
        if not result["approved"] and args.discovery_ratio and random.random() < args.discovery_ratio:
            result["approved"] = True
            result["discovery"] = True
            result["reason"] = "random discovery pick (explore)"
            result["tags"] = result.get("tags") or ["Discovery"]
        print(f"  -> Summary: {result['summary']}")
        tag = "discovery" if result.get("discovery") else "approved"
        print(f"  -> {tag.title()}: {result['approved']} ({result['reason']})\n")
        if result["approved"]:
            approved.append(result)
            if max_approved and len(approved) >= max_approved:
                print(f"Reached the approved limit ({max_approved}) — stopping.\n")
                break

    if approved:
        saved = checkpoint.save(approved, args.checkpoint)
        print(f"Saved this run to {saved}")
        _act(approved, want_epub, want_audio)
    else:
        print("No new articles matched your interest this run.")

    # Only mark the articles we actually looked at, so an early stop doesn't
    # silently skip the rest on the next run.
    if not args.no_record:
        mark_as_seen(candidates[:checked], state)


if __name__ == "__main__":
    main()
