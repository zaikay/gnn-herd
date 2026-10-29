# Researcher only: add pinned CPU baseline/evaluation dependencies.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
New-Item -ItemType Directory -Force -Path logs | Out-Null
Start-Transcript -Path logs/t02_install_baselines.log
try {
    if (-not (Test-Path -LiteralPath .venv/Scripts/python.exe)) { throw 'Existing project .venv is required' }
    & .venv/Scripts/python.exe -m pip install --no-deps --only-binary=:all: -r requirements-baselines.lock
    if ($LASTEXITCODE -ne 0) { throw 'Pinned baseline dependency install failed' }
    & .venv/Scripts/python.exe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed' }
    & .venv/Scripts/python.exe -m pip freeze
    if ($LASTEXITCODE -ne 0) { throw 'Environment inventory failed' }
} finally {
    Stop-Transcript
}
