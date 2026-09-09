# evaluation_agent.py — orchestrates scraper -> summarizer -> curator -> quiz
# for a single URL.
from article_scraper import get_article_data
from summarizer import summarize
from curator import evaluate
from quiz_agent import generate_quiz


def evaluate_article(url):
    article = get_article_data(url)
    if not article:
        return None

    summary = summarize(article["text"])
    decision = evaluate(summary)

    quiz = []
    if decision["approved"]:
        # only bother generating a quiz for articles we're actually including
        quiz = generate_quiz(article["text"])

    return {
        "url": url,
        "title": article["title"],
        "markdown": article["markdown"],   # for the EPUB body (keeps images / structure)
        "text": article["text"],           # plain text, for the podcast script
        "summary": summary,
        "approved": decision["approved"],
        "reason": decision["reason"],
        "tags": decision.get("tags", []),
        "quiz": quiz,
    }
