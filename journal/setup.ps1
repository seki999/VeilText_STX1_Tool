$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m pip install -r requirements-diary.txt

New-Item -ItemType Directory -Force -Path "private-diary\images" | Out-Null

if (-not (Test-Path "private-diary\diary.md")) {
    Copy-Item "journal\diary-template.md" "private-diary\diary.md"
}

Write-Host ""
Write-Host "VeilText private diary setup complete." -ForegroundColor Green
Write-Host "Open private-diary\diary.md in VS Code."
Write-Host "Ctrl+Shift+V: preview"
Write-Host "Ctrl+Shift+B: export current Markdown to standalone HTML"
Write-Host "Terminal -> Run Task -> VeilText Diary: Export + Encrypt current Markdown"
