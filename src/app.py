# app.py — Streamlit UI for the non-coder track.
# Editable interest prompt (can be saved back to prompts/interest.txt) + source
# list (session-only) + demo limits, a run button, a progress log, and an EPUB
# download button.
import os

import streamlit as st

import config
from discovery_agent import discover_new_articles, mark_as_seen
from evaluation_agent import evaluate_article
from publisher_agent import build_epub
from state import reset_seen

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

st.subheader("Run settings")
c1, c2 = st.columns(2)
with c1:
    max_approved = st.number_input(
        "Stop after this many approved", min_value=0, step=1,
        value=int(config.MAX_APPROVED or 0), help="Keeps a live demo short. 0 = no limit.",
    )
with c2:
    max_checked = st.number_input(
        "Check at most this many articles", min_value=0, step=1,
        value=int(config.MAX_CHECKED or 0), help="0 = no limit.",
    )
remember = st.checkbox(
    "Remember which articles were checked",
    value=True,
    help="Uncheck to re-run on the same articles next time — handy for comparing prompt tweaks.",
)
make_podcast = st.checkbox(
    "🎙️ Also make an audio podcast (spoken two-host dialogue)",
    value=False,
    help="Local Piper text-to-speech. Adds ~30–60s of scripting per article.",
)
if st.button("🔄 Forget seen articles"):
    reset_seen()
    st.toast("Cleared — the next run will re-check every article.")

if st.button("▶️ Run the agent"):
    # Push the in-session edits into config; discovery_agent and curator read
    # these attributes live, so the edits take effect for this run.
    config.SOURCES = st.session_state.sources
    config.INTEREST_PROMPT = interest_prompt
    limit_approved = int(max_approved) or None
    limit_checked = int(max_checked) or None

    with st.spinner("Discovering new articles..."):
        candidates, state = discover_new_articles()

    st.write(f"Found **{len(candidates)}** new articles to check.")

    approved = []
    checked = 0
    total = len(candidates)
    denom = min(total, limit_checked) if limit_checked else total
    progress_bar = st.progress(0)
    log = st.container()
    stop_note = None

    for c in candidates:
        if limit_checked and checked >= limit_checked:
            stop_note = f"Stopped after checking {limit_checked} article(s)."
            break
        checked += 1

        with log:
            st.markdown(f"**Checking:** {c['title']}  \n_{c['source']}_")
        try:
            result = evaluate_article(c["url"])
        except Exception as e:
            with log:
                st.markdown(f"&nbsp;&nbsp;→ error, skipping ({e})")
            progress_bar.progress(min(checked / denom, 1.0) if denom else 1.0)
            continue

        if result is None:
            with log:
                st.markdown("&nbsp;&nbsp;→ extraction failed, skipping")
            progress_bar.progress(min(checked / denom, 1.0) if denom else 1.0)
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
            if limit_approved and len(approved) >= limit_approved:
                stop_note = f"Stopped after {limit_approved} approved article(s)."
                progress_bar.progress(1.0)
                break

        progress_bar.progress(min(checked / denom, 1.0) if denom else 1.0)

    # Only remember the articles we actually looked at.
    if remember:
        mark_as_seen(candidates[:checked], state)

    if stop_note:
        st.info(stop_note)

    if approved:
        path = build_epub(approved)
        st.success(f"✅ {len(approved)} article(s) compiled!")
        with open(path, "rb") as f:
            st.download_button("⬇️ Download your EPUB", f, file_name=os.path.basename(path))

        if make_podcast:
            from narrator_agent import build_podcast, voices_available
            if not voices_available():
                st.warning(
                    "Podcast voices aren't downloaded yet. Re-run setup, or from a "
                    "terminal: `python -m piper.download_voices --download-dir voices "
                    f"{config.PODCAST_VOICE_A} {config.PODCAST_VOICE_B}`"
                )
            else:
                with st.status("Making the podcast…", expanded=True) as status:
                    audio_path = build_podcast(approved, on_progress=status.write)
                    status.update(label="Podcast ready", state="complete")
                st.audio(audio_path)
                with open(audio_path, "rb") as f:
                    st.download_button("⬇️ Download the podcast", f, file_name=os.path.basename(audio_path))
    else:
        st.warning("No articles matched your interest this run.")
