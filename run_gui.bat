@echo off
cd /d "%~dp0"
python veiltext_stx1_gui.py
if errorlevel 1 (
  echo.
  echo VeilText GUI exited with an error.
  pause
)
