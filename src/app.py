# app.py — Streamlit UI for the non-coder track.
# Editable interest prompt (can be saved back to prompts/interest.txt) + source
# list (session-only), a run button, a progress log, and an EPUB download button.
import streamlit as st

import config
from discovery_agent import discover_new_articles, mark_as_seen
from evaluation_agent import evaluate_article
from publisher_agent import build_epub

st.title("📚 Content Curator Agent")

st.subheader("What are you interested in reading about?")
interest_prompt = st.text_area(
    "Interest prompt (edit this, then click Run)",
    value=config.INTEREST_PROMPT,
    height=180,
)
if st.button("💾 Save as the default interest"):
    (config.PROMPTS_DIR / "interest.txt").write_text(interest_prompt.strip() + "\n", encoding="utf-8")
    st.toast("Saved to prompts/interest.txt")

st.subheader("Blog & feed sources")

if "sources" not in st.session_state:
    st.session_state.sources = [dict(s) for s in config.SOURCES]

for i, source in enumerate(st.session_state.sources):
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        source["name"] = st.text_input(
            f"Name {i}", value=source["name"], key=f"name_{i}", label_visibility="collapsed"
        )
    with col2:
        source["homepage"] = st.text_input(
            f"URL {i}",
            value=source.get("homepage", ""),
            key=f"url_{i}",
            label_visibility="collapsed",
        )
    with col3:
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.sources.pop(i)
            st.rerun()

if st.button("➕ Add source"):
    st.session_state.sources.append({"name": "", "homepage": "", "rss": None})
    st.rerun()

if st.button("▶️ Run the agent"):
    # Push the in-session edits into config; discovery_agent and curator read
    # these attributes live, so the edits take effect for this run.
    config.SOURCES = st.session_state.sources
    config.INTEREST_PROMPT = interest_prompt

    with st.spinner("Discovering new articles..."):
        candidates, state = discover_new_articles()

    st.write(f"Found **{len(candidates)}** new articles to check.")

    approved = []
    progress_bar = st.progress(0)
    log = st.container()

    for i, c in enumerate(candidates):
        with log:
            st.markdown(f"**Checking:** {c['title']}  \n_{c['source']}_")
        try:
            result = evaluate_article(c["url"])
        except Exception as e:
            with log:
                st.markdown(f"&nbsp;&nbsp;→ error, skipping ({e})")
            progress_bar.progress((i + 1) / len(candidates))
            continue

        if result is None:
            with log:
                st.markdown("&nbsp;&nbsp;→ extraction failed, skipping")
            progress_bar.progress((i + 1) / len(candidates))
            continue

        verdict = "✅ approved" if result["approved"] else "❌ rejected"
        with log:
            st.markdown(
                f"&nbsp;&nbsp;→ {verdict} — {result['reason']}  \n"
                f"&nbsp;&nbsp;<small>{result['summary']}</small>",
                unsafe_allow_html=True,
            )
        if result["approved"]:
            approved.append(result)

        progress_bar.progress((i + 1) / len(candidates))

    mark_as_seen(candidates, state)

    if approved:
        path = build_epub(approved)
        st.success(f"✅ {len(approved)} article(s) compiled!")
        with open(path, "rb") as f:
            st.download_button("⬇️ Download your EPUB", f, file_name="curated_reading.epub")
    else:
        st.warning("No articles matched your interest this run.")
