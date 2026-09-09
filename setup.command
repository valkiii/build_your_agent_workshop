#!/bin/bash
# One-time SETUP (Mac). Installs everything but does not launch the app.
# Handy for doing the slow AI-model download before the workshop.
# It just runs run_app.command in setup-only mode — that's the real script.
cd "$(dirname "$0")" || exit 1
exec "./run_app.command" --no-launch
