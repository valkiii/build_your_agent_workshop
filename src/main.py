# main.py — CLI orchestrator for the coder track.
# (Non-coders use app.py / the Streamlit UI instead.)
#
#   python src/main.py                     # normal run (limits from config.py)
#   python src/main.py --reset             # forget seen URLs first, re-check everything
#   python src/main.py --max-approved 3    # stop after 3 approved (0 = no limit)
#   python src/main.py --max-checked 10    # look at 10 articles at most (0 = no limit)
#   python src/main.py --no-record         # don't remember what was checked this run
#   python src/main.py --audio             # also make a spoken two-host podcast (MP3)
#   python src/main.py --audio --no-epub   # podcast only
import argparse

import config
from discovery_agent import discover_new_articles, mark_as_seen
from evaluation_agent import evaluate_article
from publisher_agent import build_epub
from state import reset_seen


def main():
    parser = argparse.ArgumentParser(description="Run the content-curation pipeline.")
    parser.add_argument("--reset", action="store_true",
                        help="forget previously-seen URLs before running (re-check everything)")
    parser.add_argument("--no-record", action="store_true",
                        help="don't save seen URLs after this run")
    parser.add_argument("--max-approved", type=int, default=config.MAX_APPROVED, metavar="N",
                        help="stop after N approved articles (0 = no limit)")
    parser.add_argument("--max-checked", type=int, default=config.MAX_CHECKED, metavar="N",
                        help="evaluate at most N articles (0 = no limit)")
    parser.add_argument("--audio", action="store_true",
                        help="also produce a spoken two-host podcast (MP3) of the approved articles")
    parser.add_argument("--no-epub", action="store_true",
                        help="skip the EPUB (pair with --audio for audio only)")
    args = parser.parse_args()

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
        print(f"  -> Summary: {result['summary']}")
        print(f"  -> Approved: {result['approved']} ({result['reason']})\n")
        if result["approved"]:
            approved.append(result)
            if max_approved and len(approved) >= max_approved:
                print(f"Reached the approved limit ({max_approved}) — stopping.\n")
                break

    if approved:
        if not args.no_epub:
            path = build_epub(approved)
            print(f"{len(approved)} articles compiled into {path}")
        if args.audio:
            from narrator_agent import build_podcast
            audio_path = build_podcast(approved, on_progress=lambda m: print(f"  [audio] {m}"))
            print(f"Podcast: {audio_path}")
    else:
        print("No new articles matched your interest this run.")

    # Only mark the articles we actually looked at, so an early stop doesn't
    # silently skip the rest on the next run.
    if not args.no_record:
        mark_as_seen(candidates[:checked], state)


if __name__ == "__main__":
    main()
