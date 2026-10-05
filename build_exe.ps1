param([string]$Python = "python")

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "== VeilText STX1 Tool: Windows single-file EXE build ==" -ForegroundColor Cyan
& $Python --version
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m pip install -r requirements-build.txt

Write-Host "Running compatibility tests..." -ForegroundColor Cyan
& $Python -m unittest -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed. EXE build aborted." }

Write-Host "Building single-file GUI EXE..." -ForegroundColor Cyan
& $Python -m PyInstaller --noconfirm --clean --onefile --windowed --name VeilText_STX1_Tool veiltext_stx1_gui.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

$exe = Join-Path $PSScriptRoot "dist\VeilText_STX1_Tool.exe"
if (-not (Test-Path $exe)) { throw "Build completed but EXE was not found: $exe" }
$hash = (Get-FileHash -Algorithm SHA256 $exe).Hash

Write-Host ""
Write-Host "Build succeeded:" -ForegroundColor Green
Write-Host "  $exe"
Write-Host "SHA256:"
Write-Host "  $hash"
