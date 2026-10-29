# Researcher only: install CUDA dependencies on the full-run laptop.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
New-Item -ItemType Directory -Force -Path logs | Out-Null
Start-Transcript -Path logs/t03_install_gnn.log
try {
    & .venv/Scripts/python.exe -m pip install --no-deps --only-binary=:all: -r requirements-gnn.lock
    if ($LASTEXITCODE -ne 0) { throw 'Pinned CUDA dependency installation failed' }
    & .venv/Scripts/python.exe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed' }
    & .venv/Scripts/python.exe -m pip freeze
    if ($LASTEXITCODE -ne 0) { throw 'Environment inventory failed' }
} finally {
    Stop-Transcript
}
