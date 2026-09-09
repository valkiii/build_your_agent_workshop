# Sample output

Finished outputs from known-good runs, kept as **facilitator backups** — if live
extraction or generation fails on the day, you can still show what success looks
like without losing momentum.

- `curated_reading_sample.epub` — 3 approved articles with topic-tag badges,
  embedded images, and a comprehension quiz per article.
- `sample_podcast.mp3` — the same idea as audio: the local LLM rewrites each
  kept article as a two-host conversation, spoken by two local Piper voices and
  stitched into one episode.
- `sample_run.json` — a checkpoint (2 kept articles). Try the "act on a saved
  run" path without curating anything first:
  `python src/main.py --from samples/sample_run.json --audio`, or upload it in
  the app's **Step 2 — Podcast**.
