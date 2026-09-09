#!/bin/bash
# ============================================================================
#  Content Curator  —  DOUBLE-CLICK THIS FILE to start the app (Mac).
#
#  The first time you run it, it installs everything it needs:
#    - Python 3 (via Homebrew, or opens the download page)
#    - Ollama   (via Homebrew, or opens the download page)
#    - the Python packages this app uses
#    - the AI model  (a few GB — this is the slow part)
#  After that, it just opens the app.
#
#  First time only: if double-clicking does nothing or shows a security
#  warning, right-click this file and choose "Open" instead.
# ============================================================================
cd "$(dirname "$0")" || exit 1

NO_LAUNCH=0
[ "$1 " = "--no-launch " ] && NO_LAUNCH=1        # setup.command calls us with this
SKIP_MODEL=0
[ -n "$CURATOR_SKIP_MODEL" ] && SKIP_MODEL=1     # CI smoke test: skip Ollama + model download

pause() { [ -t 0 ] || return 0; read -n 1 -s -r -p "Press any key to close this window..."; echo; }
have()  { command -v "$1" >/dev/null 2>&1; }

python_ok() {
  for c in python3 python3.13 python3.12 python3.11 python3.10; do
    if have "$c" && "$c" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
      PYTHON="$c"; return 0
    fi
  done
  return 1
}

# --- 1. Python 3.10+ --------------------------------------------------------
if ! python_ok; then
  echo "Python 3.10+ is not installed."
  if have brew; then
    echo "Installing Python with Homebrew..."
    brew install python@3.12
    hash -r
  fi
  if ! python_ok; then
    echo
    echo "Opening the Python download page. Install it (just run the downloaded"
    echo ".pkg), then double-click this file again to continue."
    open "https://www.python.org/downloads/" 2>/dev/null
    pause; exit 1
  fi
fi
echo "Python: $("$PYTHON" --version)"

# --- 2. Ollama -----------------------------------------------------------
if [ "$SKIP_MODEL" = "1" ]; then
  echo "Skipping Ollama + model (CURATOR_SKIP_MODEL is set)."
elif ! have ollama; then
  echo "Ollama is not installed."
  if have brew; then
    echo "Installing Ollama with Homebrew..."
    brew install --cask ollama
    hash -r
  fi
  if ! have ollama; then
    echo
    echo "Opening the Ollama download page. Install it (drag it to Applications"
    echo "and open it once), then double-click this file again to continue."
    open "https://ollama.com/download" 2>/dev/null
    pause; exit 1
  fi
fi
have ollama && echo "Ollama: $(ollama --version 2>/dev/null | head -n 1)"

# --- 3. Python packages ------------------------------------------------
if [ ! -x ".venv/bin/streamlit" ]; then
  echo "Installing Python packages (a few minutes the first time)..."
  "$PYTHON" -m venv .venv || { echo "Could not create the .venv folder."; pause; exit 1; }
  ./.venv/bin/python -m pip install --upgrade pip -q
  if ! ./.venv/bin/python -m pip install -r requirements.txt; then
    echo "Package install failed — check your internet connection and try again."
    pause; exit 1
  fi
fi

# --- 4. AI model ------------------------------------------------------
if [ "$SKIP_MODEL" != "1" ]; then
  ollama serve >/dev/null 2>&1 &                  # start the local model server if needed
  sleep 1
  MODEL=$(PYTHONPATH=src ./.venv/bin/python -c "import config; print(config.MODEL_NAME)" 2>/dev/null)
  [ -z "$MODEL" ] && MODEL="gemma4:e2b"
  if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
    echo "Downloading the AI model ($MODEL) — a few GB, one time only. Please wait..."
    ollama pull "$MODEL"
  fi

  # Text-to-speech model files for the optional audio "podcast" output.
  echo "Checking text-to-speech voices..."
  PYTHONPATH=src ./.venv/bin/python src/fetch_voices.py \
    || echo "(voice download failed — the podcast option will be unavailable)"
  # Portable ffmpeg for MP3 encoding, only if the system has none.
  command -v ffmpeg >/dev/null 2>&1 || \
    ./.venv/bin/python -c "import imageio_ffmpeg; imageio_ffmpeg.get_ffmpeg_exe()" >/dev/null 2>&1 || true
fi

# --- 5. Done / launch ------------------------------------------------
if [ "$NO_LAUNCH" = "1" ]; then
  echo
  echo "=================================================="
  echo " All done! Setup complete."
  echo "=================================================="
  echo "Next: double-click run_app.command to start the app."
  pause
  exit 0
fi

echo
echo "Starting the Content Curator — a browser tab should open in a moment."
echo "Leave this window open while you use the app. Close it (or press Ctrl+C) when done."
exec ./.venv/bin/streamlit run src/app.py
