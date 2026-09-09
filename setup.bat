@echo off
REM One-time SETUP (Windows). Installs everything but does not launch the app.
REM Handy for doing the slow AI-model download before the workshop.
REM It just runs run_app.bat in setup-only mode - that's the real script.
cd /d "%~dp0"
call "%~dp0run_app.bat" --no-launch
