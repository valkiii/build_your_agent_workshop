# main.py — CLI orchestrator for the coder track.
# (Non-coders use app.py / the Streamlit UI instead.)
from discovery_agent import discover_new_articles, mark_as_seen
from evaluation_agent import evaluate_article
from publisher_agent import build_epub


def main():
    candidates, state = discover_new_articles()
    print(f"Discovered {len(candidates)} new articles within lookback window.\n")

    approved = []
    for c in candidates:
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

    if approved:
        path = build_epub(approved)
        print(f"{len(approved)} articles compiled into {path}")
    else:
        print("No new articles matched your interest this run.")

    mark_as_seen(candidates, state)


if __name__ == "__main__":
    main()
