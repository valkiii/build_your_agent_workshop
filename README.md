# Distraction-Free Content Curator

A small **local, offline, CPU-only agentic-AI** example, built for a 3-hour hands-on
workshop. No cloud APIs, no API keys, no accounts.

The agent runs a four-step loop — **perceive → extract → decide → act**:

1. **Perceive** — read blog/RSS sources for recent articles (`src/discovery_agent.py`)
2. **Extract** — pull the article text and summarize it with a local LLM
   (`src/article_scraper.py`, `src/summarizer.py`)
3. **Decide** — judge each summary against an interest you write in plain English,
   and generate topic tags (`src/curator.py`)
4. **Act** — compile the approved articles into an **EPUB** with tags and a short
   comprehension quiz (`src/quiz_agent.py`, `src/publisher_agent.py`), or into a
   spoken **two-host podcast** (`src/narrator_agent.py`)

The interesting part isn't the code — it's that **the agent's judgment lives in a
prompt you can edit**: `prompts/interest.txt`, or the text box in the app. Tighten
it and the approve/reject decisions change.

---

## Quick start (no coding needed)

1. **Download this project** — green **Code** button → **Download ZIP** → unzip.
2. **Start it** — double-click **`run_app.command`** (Mac) or **`run_app.bat`**
   (Windows).
   - The **first run installs everything**: Python and Ollama if they're missing
     (via `winget` on Windows, Homebrew on Mac — expect a permission prompt),
     the Python packages, and the few-GB AI model. Several minutes, once.
   - *Mac without [Homebrew](https://brew.sh):* it opens the
     [Python](https://www.python.org/downloads/) and
     [Ollama](https://ollama.com/download) download pages instead — install those
     two, then double-click `run_app.command` again.
   - *Mac, first time:* if double-clicking does nothing, right-click the file →
     **Open**.
   - After that, the same double-click just opens the app in your browser.

> Running the workshop? Have participants double-click `setup.command` /
> `setup.bat` **ahead of time** so the slow model download is done before the
> session. `run_app` still works without it — it just does that setup on the
> first launch.

In the app: edit the interest prompt (optionally **Save as the default**),
add/remove sources, click **Run the agent**, then download your EPUB. Open the
EPUB in [Calibre](https://calibre-ebook.com/) (any OS), Apple Books (Mac/iOS), or
any e-reader app.

Full step-by-step in plain language:
[`docs/SIMPLE_SETUP_GUIDE.md`](docs/SIMPLE_SETUP_GUIDE.md).

---

## Project layout

```
run_app.command / run_app.bat    ◀ double-click to start (installs on first run)
setup.command   / setup.bat        optional: do the install ahead of time
requirements.txt                   the Python dependencies
prompts/                           the agent's instructions, as editable .txt files
  interest.txt                       what to keep vs. reject  (the main non-coder edit)
  summarizer.txt  curator.txt  quiz.txt
src/                               the Python code
  config.py                          model name, sources, paths, lookback window
  discovery_agent.py  article_scraper.py  summarizer.py
  curator.py  quiz_agent.py  evaluation_agent.py  publisher_agent.py
  state.py                           tracks already-seen URLs
  main.py                            CLI orchestrator (coder track)
  app.py                             Streamlit UI (non-coder track)
docs/                              workshop plan + plain-language setup guide
samples/                           an example finished EPUB (facilitator backup)
output/                            your generated EPUBs (created on first run)
state.json                         seen-URL memory (created on first run)
```

---

## For coders

```bash
python3 -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull gemma4:e2b                    # or gemma4:e4b if you have ~16GB+ RAM

python src/main.py                        # run the whole pipeline on the CLI
python src/main.py --reset                # forget seen URLs, re-check everything
python src/main.py --max-approved 3       # stop after 3 approved (0 = no limit)
python src/main.py --max-checked 10       # evaluate 10 articles at most
python src/main.py --no-record            # don't remember what was checked
python src/main.py --audio                # also make a spoken two-host podcast (MP3)
python src/main.py --audio --no-epub      # podcast only
streamlit run src/app.py                  # or run the UI
```

`src/` is put on `sys.path` when you run `src/main.py` or `streamlit run
src/app.py`, so the modules import each other by bare name (`import config`,
`from curator import evaluate`). Run any layer in isolation for debugging:

```bash
cd src
python -c "from discovery_agent import discover_new_articles; print(discover_new_articles()[0][:5])"
python -c "from summarizer import summarize; print(summarize('some article text ...'))"
```

`pyproject.toml` / `uv.lock` are provided for `uv` users and kept in sync with
`requirements.txt`; the double-click scripts use plain `venv` + `pip` so
non-coders don't need another tool.

### File map

| File | Step | What it does |
|------|------|--------------|
| `src/config.py` | — | `MODEL_NAME`, `SOURCES`, `DAYS_LOOKBACK`, `MAX_APPROVED` / `MAX_CHECKED` demo limits, output paths; loads the prompt files from `prompts/`. |
| `prompts/*.txt` | — | The system prompts, as plain text. `interest.txt` is the agent's judgment; `curator.txt` holds a `[READER_INTEREST]` placeholder filled in at run time. |
| `src/discovery_agent.py` | Perceive | RSS-first; falls back to homepage link-scraping when a feed is missing. Resolves relative URLs. |
| `src/state.py` / `state.json` | Perceive | Tracks `seen_urls` so re-runs skip already-processed articles (rejects included). Created on first run. |
| `src/article_scraper.py` | Extract | Returns plain `text` (for the model) and interleaved `markdown` (for the EPUB body, preserving image order). |
| `src/summarizer.py` | Extract | Local-LLM 2–3 sentence summary. |
| `src/curator.py` | Decide | Returns `{"approved", "reason", "tags"}` by judging the summary against `INTEREST_PROMPT`. |
| `src/quiz_agent.py` | Act | 3 comprehension Q&A pairs — only for approved articles. |
| `src/evaluation_agent.py` | — | Runs scraper → summarizer → curator → quiz for one URL. |
| `src/publisher_agent.py` | Act | Builds the EPUB: downloads images, renders tag badges and the quiz, links the title back to the source. Filename + title `Curated News of <YYYY-MM-DD>`. |
| `src/narrator_agent.py` | Act | Optional. Local LLM rewrites each approved article as a two-host dialogue (`prompts/podcast.txt`); local Piper voices speak it; the turns are stitched into one `Curated News of <date>.mp3`. |
| `src/main.py` | — | CLI orchestrator (coder track). |
| `src/app.py` | — | Streamlit UI (non-coder track). |

### Configuration

Model, sources, and timing live in `src/config.py`:

- **`MODEL_NAME`** — any small Ollama chat model. `gemma4:e2b` (lighter) or
  `gemma4:e4b` (needs more RAM). `llama3.2:3b` / `phi3` also work — `ollama pull`
  it first.
- **`SOURCES`** — list of `{"name", "rss", "homepage"}`. If `rss` is missing or
  dead, the homepage is scraped for post links instead.
- **`DAYS_LOOKBACK`** — how far back to consider articles (default 30).
- **`MAX_APPROVED`** / **`MAX_CHECKED`** — stop a run early so a live demo stays
  short (defaults 3 / 15; set to `None` to disable). Overridable per run from the
  CLI flags above and from the app's **Run settings**.
- **`PODCAST_VOICE_A` / `_B`, `PODCAST_HOST_A` / `_B`** — the two Piper voices and
  host names for the audio output. Any voice from
  `python -m piper.download_voices --help` works; setup downloads the two named
  here into `voices/`.

Prompts live in `prompts/*.txt`.

**Re-running the same articles against a tweaked prompt** (the prompt-tuning
demo): delete `state.json`, or `python src/main.py --reset`, or in the app click
**🔄 Forget seen articles** (or just untick **Remember which articles were
checked** so each run starts fresh).

---

## Audio podcast

Tick **🎙️ Also make an audio podcast** in the app, or pass `--audio` to
`main.py`. The local LLM rewrites each approved article as a back-and-forth
between two hosts, [Piper](https://github.com/OHF-Voice/piper1-gpl) speaks the
lines with two local voices, and the turns are stitched into one
`Curated News of <date>.mp3` (WAV if no ffmpeg is available — `imageio-ffmpeg`
provides a portable one). Fully offline. Piper is well over 10× real-time on CPU,
so the LLM scripting (~30–60s per article) is the slow part, not the audio.
`setup` downloads the two ~63 MB voice files into `voices/`.

## Requirements

- Python 3.10+ and [Ollama](https://ollama.com) — the `run_app` scripts install
  both on first run (`winget` on Windows, Homebrew on Mac); or install them
  yourself from the links above.
- ~10 GB free disk (mostly the model)
- Runs fully offline once set up. CPU-only is fine — expect ~10–60s per article
  for summarize + judge on a laptop CPU.

## Automated checks

`.github/workflows/smoke-test.yml` runs `setup.command` / `setup.bat` on real
macOS and Windows runners on every push: it builds the venv, installs
`requirements.txt` from clean, imports every module, and boots the Streamlit app.
The Ollama install and the multi-GB model download are skipped in CI
(`CURATOR_SKIP_MODEL=1`) — those still want a from-scratch machine to verify.

## Workshop materials

- [`docs/workshop_plan.md`](docs/workshop_plan.md) — full 3-hour plan: audience,
  timing, pedagogy, facilitator notes.
- [`docs/SIMPLE_SETUP_GUIDE.md`](docs/SIMPLE_SETUP_GUIDE.md) — participant-facing
  setup, no jargon.
- [`samples/`](samples/) — a pre-generated EPUB from a known-good run, as a
  facilitator backup if live extraction fails on the day.

## Notes and known simplifications

- Streamlit source-list edits are session-scoped, not written back to
  `config.py`. The interest prompt *can* be saved back to `prompts/interest.txt`
  with the **Save as the default** button.
- Image extraction is a pragmatic document-order DOM heuristic (filter by file
  extension, skip `.svg` icons and thumbnails), tested against a handful of real
  sites — it may need tuning for sites not yet tested.
- Articles that fail extraction are still marked "seen" so re-runs don't retry
  them forever; delete `state.json` to reset.
- Be a good web citizen: respect `robots.txt`, don't hammer sites, keep the
  source list modest.

## License

MIT — see [`LICENSE`](LICENSE).
