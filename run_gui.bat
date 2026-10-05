@echo off
cd /d "%~dp0"

if exist "dist\VeilText_STX1_Tool.exe" (
  start "" "dist\VeilText_STX1_Tool.exe"
  exit /b 0
)

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo VeilText_STX1_Tool.exe was not found and Python is not installed.
  echo.
  echo For normal use, download the Windows EXE build from GitHub Actions.
  echo For source-code recovery mode, install Python 3.10+ and run:
  echo   python -m pip install -r requirements.txt
  echo   python veiltext_stx1_gui.py
  echo.
  pause
  exit /b 1
)

python veiltext_stx1_gui.py
if errorlevel 1 (
  echo.
  echo VeilText GUI exited with an error.
  pause
)
