@echo off
REM ==========================================================================
REM  Content Curator  --  DOUBLE-CLICK THIS FILE to start the app (Windows).
REM
REM  The first time you run it, it installs everything it needs:
REM    - Python 3   (via winget)
REM    - Ollama     (via winget)
REM    - the Python packages this app uses
REM    - the AI model  (a few GB - this is the slow part)
REM  After that, it just opens the app.
REM ==========================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "NO_LAUNCH=0"
if /i "%~1"=="--no-launch" set "NO_LAUNCH=1"
REM CURATOR_SKIP_MODEL=1 (env) -> skip Ollama + the model download (used by CI smoke test)

REM Already set up? Hand straight to the no-window launcher and get out.
if not "%NO_LAUNCH%"=="1" if not defined CURATOR_SKIP_MODEL (
  if exist ".venv\Scripts\streamlit.exe" (
    start "" "%~dp0Content Curator.vbs"
    exit /b 0
  )
)

REM --- 1. Python 3.10+ ---------------------------------------------------
call :find_python
if not defined PYTHON (
  where winget >nul 2>&1
  if errorlevel 1 (
    echo Python 3.10+ is not installed, and winget is not available to install it.
    echo Install Python from https://www.python.org/downloads/
    echo ^(tick "Add python.exe to PATH" on the first screen^), then run this again.
    start "" "https://www.python.org/downloads/"
    call :pause
    exit /b 1
  )
  echo Installing Python with winget...
  winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
  set "NEED_RESTART=1"
)

REM --- 2. Ollama ---------------------------------------------------------
if defined CURATOR_SKIP_MODEL (
  echo Skipping Ollama + model ^(CURATOR_SKIP_MODEL is set^).
) else (
  where ollama >nul 2>&1
  if errorlevel 1 (
    where winget >nul 2>&1
    if errorlevel 1 (
      echo Ollama is not installed, and winget is not available to install it.
      echo Install Ollama from https://ollama.com/download , then run this again.
      start "" "https://ollama.com/download"
      call :pause
      exit /b 1
    )
    echo Installing Ollama with winget...
    winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
    set "NEED_RESTART=1"
  )
)

REM --- Freshly installed software isn't on PATH in THIS window yet ---------
if defined NEED_RESTART (
  call :find_python
  set "STILL_MISSING="
  if not defined PYTHON set "STILL_MISSING=1"
  where ollama >nul 2>&1
  if errorlevel 1 set "STILL_MISSING=1"
  if defined STILL_MISSING (
    echo.
    echo New software was installed. Please CLOSE this window and
    echo double-click this file again to finish setup.
    call :pause
    exit /b 0
  )
)

REM --- 3. Python packages ----------------------------------------------
if not exist ".venv\Scripts\streamlit.exe" (
  echo Installing Python packages ^(a few minutes the first time^)...
  "%PYTHON%" -m venv .venv
  ".venv\Scripts\python.exe" -m pip install --upgrade pip -q
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Package install failed - check your internet connection and try again.
    call :pause
    exit /b 1
  )
)

REM --- 4. AI model ---------------------------------------------------
if not defined CURATOR_SKIP_MODEL (
  start "" /b ollama serve >nul 2>&1
  set "PYTHONPATH=src"
  set "MODEL="
  for /f "delims=" %%i in ('".venv\Scripts\python.exe" -c "import config; print(config.MODEL_NAME)" 2^>nul') do set "MODEL=%%i"
  set "PYTHONPATH="
  if "!MODEL!"=="" set "MODEL=gemma4:e2b"
  ollama list 2>nul | findstr /c:"!MODEL!" >nul
  if errorlevel 1 (
    echo Downloading the AI model ^(!MODEL!^) - a few GB, one time only. Please wait...
    ollama pull !MODEL!
  )

  REM Text-to-speech model files for the optional audio "podcast" output.
  echo Checking text-to-speech voices...
  set "PYTHONPATH=src"
  ".venv\Scripts\python.exe" src\fetch_voices.py
  set "PYTHONPATH="
  REM Portable ffmpeg for MP3 encoding, only if the system has none.
  where ffmpeg >nul 2>&1 || ".venv\Scripts\python.exe" -c "import imageio_ffmpeg; imageio_ffmpeg.get_ffmpeg_exe()" >nul 2>&1
)

REM --- 5. Done / launch -------------------------------------------
if "%NO_LAUNCH%"=="1" (
  echo.
  echo ==================================================
  echo  All done! Setup complete.
  echo ==================================================
  echo Next: double-click run_app.bat to start the app.
  call :pause
  exit /b 0
)

echo.
echo Setup complete. Starting the Content Curator with no console window...
echo From now on, double-click "Content Curator.vbs" to start it.
start "" "%~dp0Content Curator.vbs"
exit /b 0

:find_python
REM Sets PYTHON to the first launcher that reports version >= 3.10.
REM (Comparison is done in batch with GEQ to avoid < > redirection characters.)
set "PYTHON="
for %%P in (python py python3) do (
  if not defined PYTHON (
    for /f "delims=" %%V in ('%%P -c "import sys;print(sys.version_info[0]*100+sys.version_info[1])" 2^>nul') do (
      if %%V GEQ 310 set "PYTHON=%%P"
    )
  )
)
goto :eof

:pause
if not defined CI pause
goto :eof
