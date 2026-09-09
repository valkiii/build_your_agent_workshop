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

# --- Sources ------------------------------------------------------------------
# Each entry: {"name", "rss", "homepage"}. If "rss" is missing or dead, the
# homepage is scraped for post links instead.
SOURCES = [
    {"name": "Google Research Blog", "rss": "https://research.google/blog/rss", "homepage": "https://research.google/blog/"},
    {"name": "DeepMind Blog", "rss": "https://deepmind.google/blog/rss.xml", "homepage": "https://deepmind.google/discover/blog/"},
    {"name": "Hacker News (front page)", "rss": "https://news.ycombinator.com/rss", "homepage": "https://news.ycombinator.com/"},
]

# --- Optional audio "podcast" output (narrator_agent.py) ---------------------
# Local Piper text-to-speech. The two voice files are downloaded by setup into
# voices/. Any voice from `python -m piper.download_voices --help` works.
VOICES_DIR = str(PROJECT_ROOT / "voices")
PODCAST_VOICE_A = "en_US-amy-medium"     # host A
PODCAST_VOICE_B = "en_US-ryan-medium"    # host B
PODCAST_HOST_A = "Amy"
PODCAST_HOST_B = "Ryan"

# --- Prompts (edit the .txt files in ../prompts/, not this file) --------------
INTEREST_PROMPT = _load_prompt("interest.txt")     # the agent's judgment, in plain English
SUMMARIZER_PROMPT = _load_prompt("summarizer.txt")
CURATOR_PROMPT = _load_prompt("curator.txt")       # contains the [READER_INTEREST] placeholder
QUIZ_PROMPT = _load_prompt("quiz.txt")
PODCAST_PROMPT = _load_prompt("podcast.txt")       # contains [HOST_A] / [HOST_B] placeholders
