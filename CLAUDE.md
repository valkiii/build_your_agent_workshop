# Content Curator Workshop — Project Context

## What this is
A teaching example for a 3-hour hands-on workshop on local, offline agentic AI (no cloud APIs, no API keys, CPU-only). This specific project is the "Distraction-Free Content Curator": it reads blog/RSS sources, has a local LLM summarize and judge each article against a stated interest, and compiles approved articles into an EPUB with topic tags and a comprehension quiz.

Full workshop context (audience, timing, pedagogy) is in `docs/workshop_plan.md`. Participant-facing setup instructions are in `docs/SIMPLE_SETUP_GUIDE.md` — if you ever touch `setup.bat`/`setup.command`/`run_app.bat`/`run_app.command`, keep them consistent with what that guide describes.

## Audience constraint (important)
Half the workshop audience does not code. Anything participant-facing must stay usable via double-click / a Streamlit UI — no terminal commands for non-coders. The coder-facing Python files can be as normal/idiomatic as needed; the *distribution* mechanism (setup scripts, app.py) is what needs to stay non-coder-friendly.

## Stack
- **LLM runtime**: Ollama, running `gemma4:e4b` (or `e2b` on lower-RAM machines) locally. No `<|think|>` token in any system prompt — thinking mode is intentionally off for speed/predictability on CPU.
- **Scraping/extraction**: `trafilatura` for plain-text extraction (feeds the summarizer), plus a custom BeautifulSoup-based DOM walk for image extraction — see note below on why.
- **UI for non-coders**: Streamlit (`src/app.py`).
- **Packaging**: `pyproject.toml` / `uv.lock` present, but participant-facing scripts use plain `venv` + `pip` (not `uv`) to avoid introducing another tool non-coders would need to install.

## Folder layout
- `src/` — all Python modules. They import each other by bare name (`import config`, `from curator import evaluate`); this works because `src/` lands on `sys.path` when you run `src/main.py` or `streamlit run src/app.py`. Do not turn this into a package with `src.` prefixes — it would break the "run each file in isolation" workshop flow.
- `prompts/` — every system prompt as a plain `.txt` file, loaded by `src/config.py` at import. Non-coders edit `prompts/interest.txt`. `prompts/curator.txt` contains a literal `[READER_INTEREST]` placeholder that `curator.py` fills in per call via `str.replace` (not `.format` — the file has literal `{ }` JSON braces).
- `docs/` — `workshop_plan.md`, `SIMPLE_SETUP_GUIDE.md`.
- `samples/` — pre-generated EPUB, facilitator backup.
- `output/`, `state.json` — generated at the project root (paths computed in `config.py` from `PROJECT_ROOT`, so they're CWD-independent). Both gitignored.
- Root scripts: `run_app.command`/`run_app.bat` (double-click to start — self-installs on first run), `setup.command`/`setup.bat` (optional ahead-of-time install). Keep all four consistent with `docs/SIMPLE_SETUP_GUIDE.md`.

## File map (all under `src/`)
- `discovery_agent.py` — Perceive step. RSS-first (`try_rss`), falls back to homepage link-scraping (`fallback_homepage_scrape`) only when no working feed exists. Filters out nav/category links via `looks_like_real_post()`. Resolves relative URLs with `urljoin` — this was a real bug once, don't regress it. Reads `config.SOURCES` / `config.DAYS_LOOKBACK` live (not `from config import`) so the Streamlit app's edits take effect.
- `state.py` / `state.json` — tracks `seen_urls` so re-runs don't re-evaluate already-processed articles (including rejected ones — rejects are marked seen too, to avoid re-summarizing them forever).
- `article_scraper.py` — Extract step. Returns both `text` (plain, for the summarizer/curator) and `markdown` (for the EPUB body, preserves paragraph breaks + image order).
  - **Important gotcha**: `trafilatura`'s own content-boundary detection (`output_format="xml"`, `<graphic>` tags) does NOT reliably include in-body images on several real sites we tested (e.g. research.google) even though it correctly extracts the surrounding paragraph text. Do not go back to trusting trafilatura for image detection — the current approach walks the raw `<body>` in document order (`find_all(["p","h2","h3","img"], recursive=True)`) to get real paragraph/image interleaving, filtered by file extension (skip `.svg` — those are consistently nav/UI icons on tested sites) and a `width-NNN` filename heuristic to skip thumbnails.
  - Image `src` values are resolved with `urljoin(page_url, src)` — personal/static-site blogs commonly use relative image paths, this was a real bug once too.
- `summarizer.py` — Extract step, LLM summarization. Prompt: `config.SUMMARIZER_PROMPT`.
- `curator.py` — Decide step. Returns `{"approved": bool, "reason": str, "tags": [...]}`. Builds its prompt per call from `config.CURATOR_PROMPT` + `config.INTEREST_PROMPT` so Streamlit edits take effect.
- `quiz_agent.py` — generates 3 comprehension Q&A pairs, only called for *approved* articles (don't waste a model call on rejects). Prompt: `config.QUIZ_PROMPT`.
- `evaluation_agent.py` — orchestrates scraper → summarizer → curator → quiz for one URL.
- `publisher_agent.py` — Act step. Builds the EPUB: downloads images (correct MIME type detected from URL extension, not hardcoded), renders tags as rounded-rectangle CSS badges, renders the quiz, makes the article title a clickable link back to the source.
- `main.py` — CLI orchestrator for the coder track (`python src/main.py`). Flags: `--reset` (clear seen URLs first), `--no-record` (don't save seen URLs), `--max-approved N` / `--max-checked N` (0 = no limit; default to the config values).
- `app.py` — Streamlit UI for the non-coder track: editable interest prompt (with a **Save as the default** button that writes `prompts/interest.txt`), editable source list (session-state only), a **Run settings** block (max-approved / max-checked number inputs, a **Remember which articles were checked** checkbox, a **🔄 Forget seen articles** button → `state.reset_seen()`), run button, progress log, EPUB download button.
- `state.py` — `load_state` / `save_state` plus `reset_seen()` (overwrites `seen_urls` with `[]` — used by `--reset` and the app button for the prompt-tuning demo).
- Early-stop semantics: both orchestrators only `mark_as_seen(candidates[:checked], ...)` — the articles actually evaluated — so a `MAX_*` stop doesn't silently skip the remainder on the next run.
- `config.py` — `MODEL_NAME`, `SOURCES`, `DAYS_LOOKBACK`, `MAX_APPROVED` / `MAX_CHECKED` (demo limits, default 3 / 15, `None` disables); `PROJECT_ROOT`/`PROMPTS_DIR`; `STATE_FILE`/`OUTPUT_DIR` (absolute, from `PROJECT_ROOT`); and `INTEREST_PROMPT` / `SUMMARIZER_PROMPT` / `CURATOR_PROMPT` / `QUIZ_PROMPT` loaded from `prompts/`.

## Known simplifications (intentional, not bugs)
- Streamlit source-list edits are session-scoped, not written back to `config.py` — fine for a single workshop session.
- Image extraction is a pragmatic DOM-order heuristic, not a universal solution — tested against a handful of real sites during development, may need adjustment for sites not yet tested.
- No image support at all in the (separate, earlier-stage) price tracker example — not part of this project.

## Distribution status
Finalized for the workshop repo:
- `requirements.txt` is the source of truth for deps; `pyproject.toml` / `uv.lock` kept in sync (coder track only).
- **`run_app.command` (Mac) / `run_app.bat` (Windows) is the single real script per platform**; `setup.*` is a 2-line shim that calls it with `--no-launch`. On first run it: finds Python 3.10+ (installs it — winget on Windows, `brew` on Mac, else opens python.org); ensures Ollama (winget / `brew --cask` / opens ollama.com); makes `.venv` + `pip install -r requirements.txt`; `ollama serve` + `ollama pull` the model from `config.py`; then `streamlit run src/app.py` (skipped with `--no-launch`). Fast on later runs. This full auto-install assumes **personal machines** (see memory `workshop-audience-personal-machines`), not locked-down corporate laptops.
  - Env hatch `CURATOR_SKIP_MODEL=1` skips the Ollama-install + model steps (CI only). `pause`/`read` are suppressed non-interactively (`[ -t 0 ]` / `if not defined CI`).
- `.github/workflows/smoke-test.yml` runs `setup.command` / `setup.bat` on `macos-latest` + `windows-latest` each push: venv, clean `requirements.txt` install, import every module, boot Streamlit. Does NOT test the winget/brew system-installs or the model pull.
- `START_HERE.txt` orients non-coders. `README.md`, `LICENSE` (MIT), `.gitignore` in place.
- `samples/curated_reading_sample.epub` is a known-good run kept as a facilitator backup.
- End-to-end verified on a fresh Python 3.12 venv: RSS discovery (Google Research + DeepMind + HN), scrape → summarize → curate → quiz → EPUB with embedded images. `gemma4:e2b` confirmed as a real public Ollama registry model (~7.2 GB).
- **Not yet tested:** the `.bat` on a real Windows machine (no Windows/Docker available here — Windows containers need a Windows host); the winget/brew system-install paths.
