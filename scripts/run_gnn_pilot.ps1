# Researcher only: CPU tests must pass before GPU use; no full-run command.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
New-Item -ItemType Directory -Force -Path logs | Out-Null
Start-Transcript -Path logs/t03_pilot.log
try {
    # A unique directory avoids permissions left by another Windows account.
    $pilotTestDirectory = 'logs/pytest-t03-' + [guid]::NewGuid().ToString('N')
    & .venv/Scripts/python.exe -m pytest -q --basetemp=$pilotTestDirectory
    if ($LASTEXITCODE -ne 0) { throw 'CPU tests failed; no GPU training started' }
    & .venv/Scripts/python.exe -m models.gnn_pilot
    if ($LASTEXITCODE -ne 0) { throw 'Pilot failed; retain logs and resumable checkpoints; do not change the protocol' }
} finally {
    Stop-Transcript
}
