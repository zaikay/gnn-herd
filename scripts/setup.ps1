# Researcher only: creates the environment and installs the exact dependency set.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
New-Item -ItemType Directory -Force -Path logs | Out-Null
Start-Transcript -Path logs/t01_environment.log
try {
    foreach ($folder in @('data/raw','data/interim','data/processed','reports/audit','reports/figures','reports/experiments','notebooks','src/features','src/models','src/evaluation')) {
        New-Item -ItemType Directory -Force -Path $folder | Out-Null
    }
    if (Test-Path -LiteralPath .venv) { throw '.venv already exists. Review it before rerunning; this script never replaces it.' }
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed' }
    & .venv/Scripts/python.exe -m pip install --no-deps --only-binary=:all: -r requirements.lock
    if ($LASTEXITCODE -ne 0) { throw 'Locked dependency install failed' }
    & .venv/Scripts/python.exe -m pip install --no-deps --no-build-isolation -e .
    if ($LASTEXITCODE -ne 0) { throw 'Project install failed' }
    & .venv/Scripts/python.exe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed' }
    & .venv/Scripts/python.exe -m pip freeze
    if ($LASTEXITCODE -ne 0) { throw 'Environment inventory failed' }
} finally {
    Stop-Transcript
}
