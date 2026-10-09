# scripts/run_all_tests.ps1
# Runs the full Student360 test suite across Backend and ML modules on Windows PowerShell

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Executing Full Student360 Unified Test Suite" -ForegroundColor Cyan
Write-Host "  Project Root: $ProjectRoot" -ForegroundColor DarkGray
Write-Host "=========================================================" -ForegroundColor Cyan

$env:PYTHONPATH = "$ProjectRoot;$BackendDir"
Set-Location $ProjectRoot

Write-Host "Running pytest across all test suites..." -ForegroundColor Yellow
pytest -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nTest suite exited with code $LASTEXITCODE" -ForegroundColor Red
}
