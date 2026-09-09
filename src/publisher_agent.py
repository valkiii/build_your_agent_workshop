# publisher_agent.py
import requests, os, re
import markdown as md
from ebooklib import epub
from config import OUTPUT_DIR

TAG_CSS = """
.tag {
    display: inline-block;
    background-color: #e8eef7;
    color: #2b4c7e;
    border-radius: 12px;
    padding: 3px 10px;
    margin: 2px 4px 8px 0;
    font-size: 0.8em;
    font-family: sans-serif;
}
.tag-container { margin-bottom: 12px; }
"""

def render_quiz(questions):
    if not questions:
        return ""
    items = "".join(
        f'<p><b>Q{i+1}:</b> {q["q"]}<br/><i>Answer:</i> <span style="color:#888">{q["a"]}</span></p>'
        for i, q in enumerate(questions)
    )
    return f'<hr/><h3>Check your understanding</h3>{items}'

def render_tags(tags):
    if not tags:
        return ""
    spans = "".join(f'<span class="tag">{t}</span>' for t in tags)
    return f'<div class="tag-container">{spans}</div>'

def build_epub(articles, filename=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = filename or os.path.join(OUTPUT_DIR, "curated_reading.epub")

    book = epub.EpubBook()
    book.set_identifier("curated-reading-list")
    book.set_title("Curated Reading List")
    book.set_language("en")

    # Embed the CSS once, shared across all chapters
    css_item = epub.EpubItem(uid="style", file_name="style/tags.css",
                              media_type="text/css", content=TAG_CSS)
    book.add_item(css_item)

    chapters = []
    for i, article in enumerate(articles):
        html_body = md.markdown(article["markdown"])

        img_urls = re.findall(r'<img[^>]+src="([^"]+)"', html_body)
        for j, img_url in enumerate(set(img_urls)):
            ext_match = re.search(r'\.(jpg|jpeg|png|gif|webp)(\?|$)', img_url, re.IGNORECASE)
            ext = ext_match.group(1).lower() if ext_match else "jpg"
            mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                    "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/jpeg")
            try:
                img_data = requests.get(img_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).content
                img_name = f"img_{i}_{j}.{ext}"
                img_item = epub.EpubItem(uid=img_name, file_name=f"images/{img_name}",
                                          media_type=mime, content=img_data)
                book.add_item(img_item)
                html_body = html_body.replace(img_url, f"images/{img_name}")
            except requests.RequestException:
                continue

        title_html = f'<h1><a href="{article["url"]}">{article["title"]}</a></h1>'
        tags_html = render_tags(article.get("tags", []))
        quiz_html = render_quiz(article.get("quiz", []))

        c = epub.EpubHtml(title=article["title"], file_name=f"chap_{i}.xhtml", lang="en")
        c.content = f"{title_html}{tags_html}{html_body}{quiz_html}"
        c.add_item(css_item)
        book.add_item(c)
        chapters.append(c)

    book.toc = chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    epub.write_epub(filename, book)
    return filename