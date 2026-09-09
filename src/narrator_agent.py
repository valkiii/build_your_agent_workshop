# narrator_agent.py — Act step (an alternative / addition to publisher_agent.py).
#
# Turns the approved articles into a single spoken two-host "podcast":
#   1. the local LLM rewrites each article as a back-and-forth dialogue script
#   2. local Piper voices speak each line (host A / host B alternate)
#   3. the lines are concatenated into one audio file (MP3 if ffmpeg is around,
#      otherwise WAV)
#
# Everything runs offline on the CPU. Piper is fast — well over 10x real-time —
# so a few minutes of audio render in seconds; the LLM scripting is the slow part.
import json
import os
import shutil
import subprocess
import wave
from datetime import date

import numpy as np
import ollama
from piper import PiperVoice

import config

_GAP_BETWEEN_TURNS = 0.35      # seconds of silence between spoken lines
_GAP_BETWEEN_ARTICLES = 0.9


def _voice_path(name):
    return os.path.join(config.VOICES_DIR, f"{name}.onnx")


def voices_available():
    return os.path.exists(_voice_path(config.PODCAST_VOICE_A)) and \
        os.path.exists(_voice_path(config.PODCAST_VOICE_B))


def _load_voices():
    if not voices_available():
        raise FileNotFoundError(
            f"Piper voice files not found in {config.VOICES_DIR}. Run setup again "
            f"(setup.command / setup.bat), or:\n"
            f"  python -m piper.download_voices --download-dir voices "
            f"{config.PODCAST_VOICE_A} {config.PODCAST_VOICE_B}"
        )
    return {
        "A": PiperVoice.load(_voice_path(config.PODCAST_VOICE_A)),
        "B": PiperVoice.load(_voice_path(config.PODCAST_VOICE_B)),
    }


def _coerce_turns(data):
    """Accept a bare list (or a dict wrapping one), normalise each turn, and make
    sure the two hosts actually alternate — small models often tag every turn the
    same, which would have one voice read both sides."""
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), None)
    if not isinstance(data, list):
        return []
    turns = []
    for t in data:
        if isinstance(t, dict) and t.get("line"):
            line = str(t["line"]).strip()
            speaker = str(t.get("speaker", "")).strip().upper()
        elif isinstance(t, str) and t.strip():
            line, speaker = t.strip(), ""
        else:
            continue
        turns.append({"speaker": "B" if speaker.startswith("B") else "A", "line": line})

    if len({t["speaker"] for t in turns}) < 2:      # model didn't really alternate
        for i, t in enumerate(turns):
            t["speaker"] = "A" if i % 2 == 0 else "B"
    return turns


def script_for_article(article):
    """Ask the local LLM to rewrite one article as [{"speaker", "line"}, ...]."""
    prompt = (config.PODCAST_PROMPT
              .replace("[HOST_A]", config.PODCAST_HOST_A)
              .replace("[HOST_B]", config.PODCAST_HOST_B))
    body = article.get("text") or article.get("markdown", "")
    user = f"Title: {article['title']}\n\n{body[:6000]}"
    resp = ollama.chat(
        model=config.MODEL_NAME,
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": user}],
        options={"num_ctx": 8192},
    )
    content = resp["message"]["content"].strip()
    content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        turns = _coerce_turns(json.loads(content))
    except json.JSONDecodeError:
        turns = []
    if not turns:  # keep the run producing audio even if the model misbehaves
        turns = [
            {"speaker": "A", "line": f"Next up: {article['title']}."},
            {"speaker": "B", "line": article.get("summary") or article["title"]},
        ]
    return turns


def _synth(voice, text):
    chunks = list(voice.synthesize(text))
    if not chunks:
        return np.zeros(0, dtype=np.int16)
    return np.concatenate([c.audio_int16_array for c in chunks])


def _to_mp3(wav_path):
    """Transcode to MP3 if any ffmpeg is available; otherwise keep the WAV."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        try:
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            return wav_path
    mp3_path = wav_path[:-4] + ".mp3"
    try:
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", wav_path,
                        "-b:a", "128k", mp3_path], check=True)
        os.remove(wav_path)
        return mp3_path
    except (subprocess.CalledProcessError, OSError):
        return wav_path


def build_podcast(articles, filename=None, on_progress=None):
    def log(msg):
        if on_progress:
            on_progress(msg)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    stamp = date.today().isoformat()
    stem = filename or os.path.join(config.OUTPUT_DIR, f"Curated News of {stamp}")
    for ext in (".mp3", ".wav"):
        if stem.endswith(ext):
            stem = stem[: -len(ext)]
    wav_path = stem + ".wav"

    voices = _load_voices()
    sr = voices["A"].config.sample_rate
    gap_turn = np.zeros(int(sr * _GAP_BETWEEN_TURNS), dtype=np.int16)
    gap_article = np.zeros(int(sr * _GAP_BETWEEN_ARTICLES), dtype=np.int16)

    n = len(articles)
    intro = (f"Welcome to Curated News for {stamp}. I'm {config.PODCAST_HOST_A}, "
             f"here with {config.PODCAST_HOST_B}. We've got {n} "
             f"{'story' if n == 1 else 'stories'} for you today.")
    segments = [_synth(voices["A"], intro), gap_article]

    for i, article in enumerate(articles, 1):
        log(f"Scripting story {i}/{n}: {article['title']}")
        turns = script_for_article(article)
        log(f"Narrating story {i}/{n} ({len(turns)} lines)")
        for turn in turns:
            segments.append(_synth(voices[turn["speaker"]], turn["line"]))
            segments.append(gap_turn)
        segments.append(gap_article)

    segments.append(_synth(voices["B"], "That's all for today. Thanks for listening."))

    full = np.concatenate([s for s in segments if len(s)])
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(full.tobytes())

    log("Encoding MP3...")
    final = _to_mp3(wav_path)
    log(f"Done ({len(full) / sr / 60:.1f} min): {final}")
    return final
