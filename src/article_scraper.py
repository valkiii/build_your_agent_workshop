# article_scraper.py — Extract step.
# Returns both `text` (plain, for the summarizer/curator) and `markdown` (for the
# EPUB body — preserves paragraph breaks and in-document image order).
#
# Why the custom DOM walk instead of trusting trafilatura for images:
# trafilatura's own content-boundary detection does NOT reliably include in-body
# images on several real sites we tested (e.g. research.google) even though it
# extracts the surrounding paragraph text fine. So we walk the raw <body> in
# document order to get real paragraph/image interleaving, filtered by file
# extension (only .png/.jpg/.jpeg/.webp — .svg is consistently nav/UI icons) and
# a `width-NNN` filename heuristic to skip thumbnails.
import re

import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin

CONTENT_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
STOP_MARKERS = [
    "other posts of interest",
    "follow us",
    "explore our other initiatives",
    "related posts",
    "more from",
]


def strip_images(markdown_text):
    return re.sub(r"!\[.*?\]\(.*?\)", "", markdown_text)


def build_interleaved_markdown(html, page_url, min_width=300, min_paragraph_len=40):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup

    raw_parts = []
    seen_images = set()

    for el in body.find_all(["p", "h2", "h3", "img"], recursive=True):
        if el.name == "img":
            src = el.get("src") or el.get("data-src")
            if not src:
                continue
            src = urljoin(page_url, src)  # resolve relative paths like /images/foo.png
            clean_src = src.split("?")[0]  # strip query params before checking extension
            if src in seen_images or not clean_src.lower().endswith(CONTENT_EXTENSIONS):
                continue
            width_match = re.search(r"width-(\d+)", src)
            if width_match and int(width_match.group(1)) < min_width:
                continue
            seen_images.add(src)
            raw_parts.append(("img", f"![]({src})"))
        else:
            text = el.get_text(strip=True)
            if text:
                kind = "heading" if el.name in ("h2", "h3") else "p"
                raw_parts.append((kind, f"## {text}" if kind == "heading" else text))

    start = next(
        (
            i
            for i, (kind, txt) in enumerate(raw_parts)
            if kind == "p" and len(txt) >= min_paragraph_len
        ),
        0,
    )
    end = len(raw_parts)
    for i, (kind, txt) in enumerate(raw_parts[start:], start=start):
        if any(marker in txt.lower() for marker in STOP_MARKERS):
            end = i
            break

    return "\n\n".join(txt for _, txt in raw_parts[start:end])


def get_article_data(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        return None

    plain_text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not plain_text:
        return None

    metadata = trafilatura.extract_metadata(downloaded)
    title = metadata.title if metadata and metadata.title else url

    interleaved_markdown = build_interleaved_markdown(downloaded, url)

    return {
        "title": title,
        "markdown": interleaved_markdown or plain_text,
        "text": plain_text,
    }
