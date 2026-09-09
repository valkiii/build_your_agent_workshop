# Local Agentic AI Workshop — Full Plan

**Format:** 3 hours, mixed coder/non-coder audience
**Core exercise:** Distraction-Free Content Curator (RSS → LLM summarize → LLM decide → EPUB with tags/quiz)
**Everything runs locally, offline, CPU-only.**

---

## 1. Pre-Workshop Preparation

### 1a. Collecting laptop specs beforehand

You need this to decide, per person, whether they run `gemma4:e2b` (lighter) or `e4b` (default), and to flag anyone on a locked-down corporate laptop before the day.

**Recommended: a simple Google Form.** Reliable, works before people arrive, zero hosting risk. Fields to collect:
- Name
- OS (macOS / Windows / Linux)
- RAM (8GB / 16GB / 32GB+)
- Chip (Apple Silicon / Intel / AMD)
- Free disk space (rough estimate — need ~10GB free)
- Admin rights on this laptop? (yes/no — corporate laptops are the #1 risk)
- Do you already code? (yes/no — for pairing/grouping)
- Do you have an e-reader or tablet, or will you read on this laptop?

**Alternative: host it yourself on the Raspberry Pi**, if you want the whole exercise — including collecting sign-ups — to be "local-first," matching the workshop's theme. The catch: for people to fill it out *before* the event, the Pi needs to be reachable from the outside, not just your home network. Two ways to do that:
- **Cloudflare Tunnel** (free, no port forwarding, no static IP needed) — run `cloudflared tunnel` on the Pi, get a public URL, point a simple Flask app + SQLite behind it.
- **Only if the form only needs to work on the workshop day itself** (e.g., a "check in" step, not pre-work), a plain local-network Flask app on the Pi is enough, since everyone will be on the venue wifi by then.

If you want, I can build you the actual Flask app + HTML form for this separately — it's a nice self-contained artifact (and could even double as a bonus 4th "look what a tiny local agent-adjacent tool looks like" example for the workshop itself). Given prep-time constraints though, I'd default to the Google Form and treat the Pi version as a nice-to-have, not a dependency.

### 1b. Installation checklist to send participants (~1 week before)

The project repo includes a **Simple Setup Guide** (`SIMPLE_SETUP_GUIDE.md`) plus one double-click script per platform (`run_app.bat` for Windows, `run_app.command` for Mac). On first run it installs **everything** — Python, Ollama, the Python packages, and the AI model — then launches the app; non-coders never type a command. (`setup.bat` / `setup.command` do the same install without launching, for getting the slow model download done ahead of time.) This assumes personal machines; on a locked-down corporate laptop the system installs will need admin rights. Send the guide directly.

**For everyone:**
```
[ ] Workshop code downloaded: visit the repo link, click the green "Code"
    button, click "Download ZIP", unzip it
[ ] Double-clicked setup.bat (Windows) / setup.command (Mac) ahead of time,
    waited for "All done! Setup complete" (installs Python + Ollama if missing,
    then downloads the AI model — a few GB, several minutes, this is normal)
      - Windows: approve the winget / User Account Control prompt
      - Mac without Homebrew: the script opens the Python + Ollama download
        pages — install those two, then double-click the script again
[ ] Double-clicked run_app.bat / run_app.command — a browser tab opened
    showing the app
[ ] Calibre installed (calibre-ebook.com) — see note on e-readers below
```

**Additionally for the coders' track:**
```
[ ] VS Code installed with the Python extension
```

**Mac-specific note to include in the invite**: if double-clicking `setup.command` or `run_app.command` does nothing, right-click the file and choose "Open" instead (a one-time macOS security step for downloaded files). Worth testing this yourself on an actual Mac beforehand — ZIP downloads can sometimes strip the file's "executable" permission, which would need a single one-time terminal command (`chmod +x setup.command run_app.command`) to fix. Confirm this works cleanly before relying on it for the whole room.

Since this workshop dropped the price tracker, there's **no Telegram setup, no API keys, no external accounts needed at all** — genuinely the lightest pre-work version of everything we've discussed. Worth saying explicitly in your invite email; it lowers the activation energy for people on the fence about attending.

### 1c. What to read the final EPUB on

This needs an explicit recommendation, since "just open the EPUB" doesn't work out of the box on every device:

- **Best universal fallback, works for everyone regardless of device: install Calibre** (free, Win/Mac/Linux) beforehand. Guaranteed to open the file, and it's itself a nice example of "local, open, non-cloud" software fitting the workshop's theme.
- **Mac/iOS users**: Apple Books opens EPUBs natively, no install needed.
- **Android users**: Google Play Books, or any EPUB reader app (Moon+ Reader is a common free one).
- **If someone brings a Kobo e-reader**: works natively, EPUB is Kobo's native format — a nice showcase device if anyone has one, worth asking in the form.
- **If someone brings a Kindle**: flag this explicitly — Kindles do **not** natively read EPUB (they use AZW/MOBI/KFX). They'd need to convert via Calibre or "Send to Kindle" first. Worth a one-line warning in the pre-work email so nobody's surprised on the day.

---

## 2. Presentation (~30–35 min, start of session)

Keep this tight — the goal is just enough shared vocabulary before hands-on, not a lecture.

**Slide block A — What is an agent, really? (~10 min)**
- Contrast: a chatbot answers; an agent *perceives → extracts → decides → acts*, often in a loop, often using tools.
- Walk through the loop using the Content Curator as the running example, before anyone's touched a keyboard: "it reads a feed (perceive), summarizes each article (extract), judges it against your interest (decide), builds a book (act)."
- One live example on screen: paste a scraped article into the plain Ollama chat window, ask it to summarize — "this is the model. An agent is this model, wired into a loop, calling tools."

**Slide block B — Why local? (~5 min)**
- Privacy (nothing leaves the laptop), cost (free after setup), offline capability, and — honestly — the discipline of small-model constraints teaches better prompt/tool design than always reaching for a huge cloud model.

**Slide block C — Do's and Don'ts of agents (~10–15 min)**
This is the most important content block — pull directly from what you actually hit while building this:
- **Don't blindly trust model judgment on consequential actions** — tie back to the price-tracker "pause before buying" discussion if you mention it at all, or reframe here as "would you let this agent delete files / spend money without confirmation?"
- **Check for structured data before reaching for an LLM** — the JSON-LD/RSS lesson: agents should use the cheapest reliable tool for the job, not the model for everything.
- **Small local models need explicit, structured prompting** — the JSON-parsing fragility, the `<|think|>` token tradeoff, the "return ONLY valid JSON" rule — these aren't edge cases, they're the normal experience of working with CPU-friendly models.
- **State and memory matter** — the "mark as seen" design choice (don't re-evaluate rejected articles forever) as a concrete example of agent memory design.
- **Real-world scraping has real-world messiness** — relative URLs, JS-rendered content, inconsistent HTML — agents built against the real internet need defensive coding, not happy-path code.

---

## 3. Hands-On Session (~2 hours)

### Track split
- **Non-coders**: no pipeline-building tool at all — instead, a physical "be the agent" exercise, then hands-on prompt tuning inside the Streamlit app (they author the agent's judgment in plain English, without needing to understand orchestration).
- **Coders**: the Python files directly, extending features.
- Seat mixed pairs/tables where possible — a non-coder next to a coder makes for good informal peer support and keeps both engaged with the same underlying concepts.

**Why no visual pipeline builder**: building a pipeline in any tool (n8n, Flowise, etc.) risks becoming "learn this tool's UI" rather than "understand the agent loop." The flow itself gets explained and demonstrated live — non-coders don't need to construct one themselves to understand it.

### Suggested timeline

**0:00–0:15 — "Be the agent" physical relay (whole room, together)**
Small groups of 4, printed article, paper roles: **Scout** (reads it, gets the gist), **Summarizer** (writes 2 sentences), **Judge** (checks the summary against a written interest statement, approves/rejects with a reason), **Publisher** (writes the approved summary onto a shared page). Run it once as a literal relay. Zero setup, zero debugging risk, makes perceive→extract→decide→act a lived experience before anyone touches a laptop — works identically for coders and non-coders, good shared moment before the tracks split.

**0:15–0:40 — Guided build (tracks split)**
- Non-coders: watch a live walkthrough of the Streamlit app and the plain Ollama chat window — "this is the model, this is the prompt driving each step."
- Coders: walk through the actual Python files in `src/` (`discovery_agent.py` → `evaluation_agent.py` → `publisher_agent.py`), running each in isolation first (`cd src` then `python -c "..."`), same debugging-by-layer approach used throughout development. The system prompts live as plain-text files in `prompts/`.

**0:40–0:55 — "You vs. the model" exercise (whole room, together)**
Hand out 3 pre-written article summaries. Everyone privately decides approve/reject against a shared interest prompt, then compares to what the model actually decided. Discuss disagreements as a group — this is your best concept-solidifying moment and needs zero setup or debugging risk.

**0:55–1:10 — Break**

**1:10–1:40 — Prompt-tuning exercise (non-coders) / own extension (coders)**
- Non-coders: structured rounds tuning the actual system prompts — start with a deliberately vague interest prompt in the Streamlit app, watch it approve too much; tighten it over 2–3 rounds and watch decisions change each round. This is their real "build" — authoring the agent's judgment in plain English, no orchestration required. Add/remove sources with the editor too.
- Coders: pick an extension to build — add a new RSS source, tune the tag-generation prompt, or attempt the quiz feature if not already wired in. Offer 2–3 concrete "stretch goal" options so nobody stalls on a blank page.

**1:40–2:10 — Run it end-to-end + "break it and see what happens"**
Everyone runs their tuned version on a real feed via the Streamlit app (non-coders) or `python src/main.py` (coders), downloads the EPUB. Then deliberately mistune the interest prompt (too strict / too loose) and rerun against the same articles — watch decisions flip. Good energy moment, reinforces that judgment lives in the prompt, not magic.

**2:10–2:30 — Read the result + regroup**
Everyone loads their own EPUB into Calibre/Apple Books/their e-reader and actually reads a page — a genuinely satisfying close, since it's a real object they made, not just terminal output. Coders and non-coders regroup to compare what they each built.

**2:30–2:45 — Discussion + wrap-up**
Revisit the Do's/Don'ts slide with real examples from what just happened in the room ("remember when X's agent approved something weird? let's look at why"). Point coders and non-coders alike toward extending this further on their own.

**2:45–3:00 — Buffer**
Always keep this — something will run long, and it's better as float time than cut from the wrap-up discussion.

---

## 4. Other things worth planning for

- **Facilitator backup plan**: pre-generate one finished EPUB from a known-good run, so if live extraction fails on the day for a specific source, you can still show "here's what success looks like" without losing momentum.
- **Cached fallback pages**: save 2–3 article HTML pages locally (same idea as earlier in this build process) in case venue wifi struggles under everyone hitting the same feeds simultaneously.
- **Printed one-page reference card**: the interest-prompt tuning steps for non-coders, file/function names for Python coders — lets people who fall behind catch up without interrupting you.
- **Power strips**: 3-hour laptop-heavy session, plan for outlets per table.
- **A designated helper/TA**, if you can get one — a room this hands-on with a mixed-skill audience benefits enormously from a second person circulating during build time while you keep pace at the front.
- **Post-workshop takeaway**: a GitHub repo with all the final Python code and this plan, so people can keep building after the session ends.
- **Set up the repo before sending the pre-work email, not after**: it needs to contain the working code, `SIMPLE_SETUP_GUIDE.md`, and the four setup/run scripts (`setup.bat`, `setup.command`, `run_app.bat`, `run_app.command`) at the repo root, since the pre-work checklist points participants straight at it. Test the "download ZIP → double-click setup → double-click run" flow yourself, on a machine that's never had the project installed, before trusting it for the room.
- **A short feedback form at the end** — genuinely useful for tuning the next run of this workshop, and cheap to set up (same Google Form pattern as the intake form).
- **Ethics/ToS note**: worth one explicit slide or spoken aside on scraping etiquette (robots.txt, rate limiting, not hammering a site) — relevant content, not just a legal CYA.
- **Group size assumption**: this plan assumes a moderate group (~12–20). If it's meaningfully bigger, the "you vs. the model" and debrief discussions will need structuring (e.g., small groups reporting back) rather than open floor, since that breaks down past ~20 people.
