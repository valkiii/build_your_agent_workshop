# fetch_voices.py — download the text-to-speech model files for the engine set
# in config.TTS_ENGINE, into voices/. Safe to re-run: it skips files already
# present. Called by setup.command / setup.bat.
#
#   python src/fetch_voices.py
import os
import subprocess
import sys

import requests

import config

_KOKORO_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
_KOKORO_FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]   # ~310 MB + ~27 MB


def _download(url, dest):
    tmp = dest + ".part"
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        done = 0
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r  {os.path.basename(dest)}  {done * 100 // total}%", end="", flush=True)
    os.replace(tmp, dest)
    print()


def _fetch_kokoro():
    for name in _KOKORO_FILES:
        dest = os.path.join(config.VOICES_DIR, name)
        if os.path.exists(dest):
            continue
        _download(f"{_KOKORO_BASE}/{name}", dest)


def _fetch_piper():
    subprocess.run(
        [sys.executable, "-m", "piper.download_voices",
         "--download-dir", config.VOICES_DIR,
         config.PIPER_VOICE_A, config.PIPER_VOICE_B],
        check=True,
    )


def main():
    os.makedirs(config.VOICES_DIR, exist_ok=True)
    engine = config.TTS_ENGINE.lower()
    print(f"Fetching '{engine}' voice model files into {config.VOICES_DIR} ...")
    (_fetch_kokoro if engine == "kokoro" else _fetch_piper)()
    print("Voices ready.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # non-fatal for setup — the podcast option just stays off
        print(f"Voice download failed ({e}). The podcast option will be unavailable "
              f"until you run: python src/fetch_voices.py")
        sys.exit(1)
