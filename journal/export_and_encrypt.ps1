param(
    [Parameter(Mandatory=$true)]
    [string]$MarkdownFile
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    & "$PSScriptRoot\setup.ps1"
}

& $Python "$PSScriptRoot\export_single_html.py" $MarkdownFile
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$InputPath = [System.IO.Path]::GetFullPath($MarkdownFile)
$Directory = [System.IO.Path]::GetDirectoryName($InputPath)
$Stem = [System.IO.Path]::GetFileNameWithoutExtension($InputPath)
$HtmlPath = Join-Path $Directory ($Stem + ".single.html")
$EncryptedPath = Join-Path $Directory ($Stem + ".stx1")

& $Python "$PSScriptRoot\encrypt_html.py" $HtmlPath $EncryptedPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Remove-Item $HtmlPath -Force
Write-Host ""
Write-Host "Encrypted diary saved to: $EncryptedPath" -ForegroundColor Green
Write-Host "Temporary plaintext HTML removed."
