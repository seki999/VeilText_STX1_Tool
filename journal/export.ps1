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
