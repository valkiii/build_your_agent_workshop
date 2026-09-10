# config.py — the knobs.
# Non-coders mainly edit the plain-text files in ../prompts/ (especially
# interest.txt) and the SOURCES list below.
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def _load_prompt(filename):
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


# --- Local model ----------------------------------------------------------------
# Any small Ollama chat model. "gemma4:e2b" is the lighter build for lower-RAM
# machines; use "gemma4:e4b" if you have ~16GB+ RAM. "llama3.2:3b" / "phi3" also
# work — `ollama pull` it first.
MODEL_NAME = "gemma4:e2b"

# --- Where generated files go (kept at the project root, not inside src/) -------
DAYS_LOOKBACK = 30
STATE_FILE = str(PROJECT_ROOT / "state.json")
OUTPUT_DIR = str(PROJECT_ROOT / "output")

# --- Demo limits --------------------------------------------------------------
# Keep a live demo short: stop a run early instead of grinding through every
# article on a CPU. Set either to None (or 0 in the app / CLI) to disable.
MAX_APPROVED = 3      # stop once this many articles have been approved
MAX_CHECKED = 15     # evaluate at most this many articles per run

# Epsilon-greedy "exploration": this fraction of evaluated articles is kept at
# random, regardless of the interest match — to surface topics you didn't ask
# for. 0.0 = off. Tweakable in the app.
DISCOVERY_RATIO = 0.0

# Stop the local server this many seconds after the browser tab is closed (so a
# background launch doesn't linger). 0 = never auto-stop.
AUTO_SHUTDOWN_SECONDS = 30

# --- Sources ------------------------------------------------------------------
# Each entry: {"name", "rss", "homepage"}. If "rss" is missing or dead, the
# homepage is scraped for post links instead.
SOURCES = [
    {"name": "Google Research Blog", "rss": "https://research.google/blog/rss", "homepage": "https://research.google/blog/"},
    {"name": "DeepMind Blog", "rss": "https://deepmind.google/blog/rss.xml", "homepage": "https://deepmind.google/discover/blog/"},
    {"name": "Hacker News (front page)", "rss": "https://news.ycombinator.com/rss", "homepage": "https://news.ycombinator.com/"},
]

# --- Optional audio "podcast" output (narrator_agent.py) ---------------------
# Model files are downloaded by setup into voices/ (see src/fetch_voices.py).
VOICES_DIR = str(PROJECT_ROOT / "voices")

# "kokoro" — natural neural voices, ~3x real-time on CPU, ~340 MB of model files.
# "piper"  — robotic but tiny (~130 MB) and ~15x real-time; fallback for slow /
#            low-RAM machines.
TTS_ENGINE = "kokoro"
PODCAST_SPEED = 1.0                      # 1.0 = normal; <1 slower, >1 faster
PODCAST_HOST_A = "Maya"
PODCAST_HOST_B = "Ethan"

KOKORO_VOICE_A = "af_heart"              # host A (see `Kokoro(...).get_voices()` for the full list)
KOKORO_VOICE_B = "am_michael"            # host B
PIPER_VOICE_A = "en_US-amy-medium"       # used only when TTS_ENGINE = "piper"
PIPER_VOICE_B = "en_US-ryan-medium"

# --- Prompts (edit the .txt files in ../prompts/, not this file) --------------
INTEREST_PROMPT = _load_prompt("interest.txt")     # the agent's judgment, in plain English
SUMMARIZER_PROMPT = _load_prompt("summarizer.txt")
CURATOR_PROMPT = _load_prompt("curator.txt")       # contains the [READER_INTEREST] placeholder
QUIZ_PROMPT = _load_prompt("quiz.txt")
PODCAST_PROMPT = _load_prompt("podcast.txt")       # contains [HOST_A] / [HOST_B] placeholders
ASSISTANT_PROMPT = _load_prompt("assistant.txt")   # the "help me set up" chat helper
REFINE_PROMPT = _load_prompt("refine.txt")         # rewrite the interest prompt from feedback
