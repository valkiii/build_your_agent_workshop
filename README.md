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
   - After the first run, use the launcher it creates — **`Content Curator.app`**
     (Mac) / **`Content Curator.vbs`** (Windows). No terminal window: it starts
     the server in the background, opens your browser, and the server stops
     itself a little after you close the tab (or use the **⏻ Quit** button in the
     app's sidebar).

> Running the workshop? Have participants double-click `setup.command` /
> `setup.bat` **ahead of time** so the slow model download is done before the
> session. `run_app` still works without it — it just does that setup on the
> first launch.

In the app: not sure what to put? Open **🤖 New here?** and chat with the local
model — it drafts an interest prompt and suggests blogs you can apply with one
click. Otherwise edit the interest prompt and sources yourself, hit **💾 Save my
setup** so it sticks next time, click **Run the agent**, then download your EPUB.
Open the EPUB in [Calibre](https://calibre-ebook.com/) (any OS), Apple Books
(Mac/iOS), or any e-reader app.

Full step-by-step in plain language:
[`docs/SIMPLE_SETUP_GUIDE.md`](docs/SIMPLE_SETUP_GUIDE.md).

---

## Project layout

```
run_app.command / run_app.bat    ◀ double-click to start (installs on first run)
setup.command   / setup.bat        optional: do the install ahead of time
Content Curator.vbs                Windows no-window launcher (Mac makes a .app on first run)
requirements.txt                   the Python dependencies
prompts/                           the agent's instructions, as editable .txt files
  interest.txt                       what to keep vs. reject  (the main non-coder edit)
  summarizer.txt  curator.txt  quiz.txt  podcast.txt  assistant.txt  refine.txt
src/                               the Python code
  config.py                          model, sources, paths, limits, TTS settings
  discovery_agent.py  article_scraper.py  summarizer.py
  curator.py  quiz_agent.py  evaluation_agent.py
  publisher_agent.py                 Act: build the EPUB
  narrator_agent.py  fetch_voices.py  Act: build the audio podcast
  checkpoint.py                      save/load a run so Act steps can be redone
  assistant.py  settings.py          the "🤖 New here?" chat; persisted user setup
  feedback.py  autoquit.py           rate picks -> refine prompt; browser-close shutdown
  state.py                           tracks already-seen URLs
  main.py                            CLI orchestrator (coder track)
  app.py                             Streamlit UI (non-coder track)
docs/                              workshop plan + plain-language setup guide
samples/                           example EPUB, podcast, and a checkpoint
output/                            generated EPUB / MP3 / checkpoint (first run)
voices/  state.json                TTS models, seen-URL memory
my_settings.json  feedback.json    saved setup, and your keep/drop ratings
```

---

## For coders

```bash
python3 -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull gemma4:e2b                    # or gemma4:e4b if you have ~16GB+ RAM

python src/main.py                        # curate + EPUB, and save a checkpoint
python src/main.py --audio                # curate + podcast instead
python src/main.py --epub --audio         # curate + both
python src/main.py --reset                # forget seen URLs, re-check everything
python src/main.py --max-approved 3       # stop after 3 approved (0 = no limit)
python src/main.py --max-checked 10       # evaluate 10 articles at most
python src/main.py --no-record            # don't remember what was checked
python src/main.py --discovery-ratio 0.15 # also keep ~15% of articles at random
streamlit run src/app.py                  # or run the UI

# second step: act on a saved run without re-curating
python src/main.py --from "output/Curated News of 2026-09-09.json" --audio
```

Every normal run writes a **checkpoint** — `output/Curated News of <date>.json`,
the list of kept articles. `--from FILE` skips discovery and the LLM entirely and
just (re)builds the EPUB / podcast from it, so you can curate once and produce
the audio later (or on another machine). The app does the same as its
**Step 1 — Curate** / **Step 2 — Podcast** sections.

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
| `src/checkpoint.py` | — | Save / load the kept articles of a run (`output/…​.json`) so the Act steps can be re-run later without re-curating. |
| `src/publisher_agent.py` | Act | Builds the EPUB: downloads images, renders tag badges and the quiz, links the title back to the source. Filename + title `Curated News of <YYYY-MM-DD>`. |
| `src/narrator_agent.py` | Act | Optional. Local LLM rewrites each approved article as a two-host dialogue (`prompts/podcast.txt`); a local TTS engine (Kokoro or Piper, `config.TTS_ENGINE`) speaks it; the turns are stitched into one `Curated News of <date>.mp3`. |
| `src/fetch_voices.py` | — | Downloads the TTS model files for `config.TTS_ENGINE` into `voices/`. Run by setup; safe to re-run. |
| `src/assistant.py` | — | The "🤖 New here?" chat: streams a reply from the local model (`prompts/assistant.txt`) and extracts a suggested interest prompt + source list. |
| `src/settings.py` | — | Persists the app's interest prompt + source list to `my_settings.json` so they survive a restart (`config.py` values are the fallback). |
| `src/feedback.py` | — | Stores 👍/👎 ratings (`feedback.json`) and asks the model to rewrite the interest prompt from them (`prompts/refine.txt`). |
| `src/autoquit.py` | — | Daemon thread that stops the server ~`AUTO_SHUTDOWN_SECONDS` after the last browser tab closes; also backs the sidebar **⏻ Quit** button. |
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
- **`DISCOVERY_RATIO`** — epsilon-greedy exploration: fraction of articles kept
  at random regardless of the interest match (default 0.0). Slider in the app,
  `--discovery-ratio` on the CLI.
- **`AUTO_SHUTDOWN_SECONDS`** — stop the local server this long after the browser
  tab closes (default 30; 0 = never).
- **`TTS_ENGINE`** (`kokoro` / `piper`), **`KOKORO_VOICE_A` / `_B`** (or
  `PIPER_VOICE_A` / `_B`), **`PODCAST_HOST_A` / `_B`**, **`PODCAST_SPEED`** — the
  audio output. Switching `TTS_ENGINE` and re-running `setup` (or
  `python src/fetch_voices.py`) fetches the right model files.

Prompts live in `prompts/*.txt`.

**Re-running the same articles against a tweaked prompt** (the prompt-tuning
demo): delete `state.json`, or `python src/main.py --reset`, or in the app click
**🔄 Forget seen articles** (or just untick **Remember which articles were
checked** so each run starts fresh).

---

## Audio podcast

In the app: **Step 2 — Podcast** (on this session's run, or a checkpoint file you
upload). On the CLI: `python src/main.py --audio`, or
`python src/main.py --from "<checkpoint>.json" --audio` to make it from an earlier
run.

The local LLM rewrites each kept article as a back-and-forth between two hosts, a
local text-to-speech engine speaks the lines with two voices, and the turns are
stitched into one `Curated News of <date>.mp3` (WAV if no ffmpeg is available —
`imageio-ffmpeg` provides a portable one). Fully offline.

Two engines, set by `config.TTS_ENGINE`:

- **`kokoro`** (default) — [Kokoro](https://github.com/thewh1teagle/kokoro-onnx),
  an 82M Apache-2.0 model. Natural voices; ~3× real-time on CPU; ~340 MB of model
  files. Voice list: any name in `Kokoro(...).get_voices()`.
- **`piper`** — [Piper](https://github.com/OHF-Voice/piper1-gpl). Robotic but
  tiny (~130 MB) and ~15× real-time — for slow or low-RAM machines.

`setup` runs `src/fetch_voices.py`, which downloads whatever the chosen engine
needs into `voices/`. `samples/sample_run.json` is a checkpoint you can try
`--from` on without curating anything first.

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

- The app's interest prompt + source-list edits persist between runs in
  `my_settings.json` (gitignored) once you click **💾 Save my setup** — applying
  the assistant's suggestions or a **📝 Review & refine** both save automatically.
  **↩️ Back to the example** clears it. `config.INTEREST_PROMPT` / `config.SOURCES`
  are the fallback.
- The no-window launcher + auto-shutdown are best-effort. Mac: the generated
  `.app` is unquarantined so it opens clean, but the *first* `run_app.command`
  still needs the one-time right-click→Open and may ask permission to close its
  Terminal window. Windows: `Content Curator.vbs` from a ZIP shows a one-time
  "Open File - Security Warning". Auto-shutdown uses a private Streamlit API
  (guarded — if it breaks, use the **⏻ Quit** button).
- Image extraction is a pragmatic document-order DOM heuristic (filter by file
  extension, skip `.svg` icons and thumbnails), tested against a handful of real
  sites — it may need tuning for sites not yet tested.
- Articles that fail extraction are still marked "seen" so re-runs don't retry
  them forever; delete `state.json` to reset.
- Be a good web citizen: respect `robots.txt`, don't hammer sites, keep the
  source list modest.

## License

MIT — see [`LICENSE`](LICENSE).
