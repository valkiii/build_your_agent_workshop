# Getting Ready for the Workshop — Simple Guide

No coding experience needed. Set aside about 20 minutes — mostly waiting for downloads.

---

## Step 1 — Download the workshop project

1. Go to the link your workshop organizer gave you (a GitHub page)
2. Click the green **"Code"** button, then **"Download ZIP"**
3. Find the ZIP (usually in your Downloads folder) and unzip it — on Mac,
   double-click it; on Windows, right-click → "Extract All"
4. Move the unzipped folder somewhere easy to find, like your Desktop

---

## Step 2 — Run it

Open the folder and double-click:

- **Windows**: `run_app.bat`
- **Mac**: `run_app.command`
  *(First time only: if double-clicking does nothing or shows a security
  warning, right-click the file instead → **"Open"** → confirm. A one-time
  macOS step for downloaded files.)*

A black window opens and shows progress. **The first time, it sets everything
up for you:**

- installs **Python** and **Ollama** (the program that runs the AI) if you don't
  already have them
- installs the small pieces of code the app needs
- downloads the **AI model** — a few gigabytes, so this part takes several
  minutes. This is normal.

You may see a permission pop-up ("Do you want to allow this app to make
changes?") while Python or Ollama installs — click **Yes** / enter your password.

**On Mac without [Homebrew](https://brew.sh):** the window will instead open the
Python and Ollama download pages. Install those two (normal double-click
installers — on the Python one there's nothing special to tick on Mac), then
double-click `run_app.command` again. It handles everything else.

When a browser tab opens with the app, you're ready.

---

## Step 3 — From now on

The first run leaves a launcher next to the other files:

- **Mac**: `Content Curator.app`
- **Windows**: `Content Curator.vbs`

Double-click that to start the app **with no black window** — it opens straight
in your browser. The app shuts itself down a little after you close the browser
tab, or you can click **⏻ Quit the app** in the sidebar.

---

## Doing it ahead of time (recommended)

The AI-model download is the slow part. To get it out of the way before the
session, double-click **`setup.bat`** (Windows) / **`setup.command`** (Mac)
instead — same setup, but it stops when it's done rather than opening the app.
When it says **"All done! Setup complete"**, you're set.

---

## Something not working?

Bring your laptop as-is to the workshop — we'll have time set aside to help
anyone who gets stuck, and it's common for one step to need a small fix on the day.
