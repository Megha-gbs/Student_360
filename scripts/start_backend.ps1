# scripts/start_backend.ps1
# Starts the Student360 FastAPI Backend Server on Windows PowerShell

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Starting Student360 FastAPI Backend Server" -ForegroundColor Cyan
Write-Host "  Project Root: $ProjectRoot" -ForegroundColor DarkGray
Write-Host "=========================================================" -ForegroundColor Cyan

# Check if port 8000 is already in use
$existingConn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($existingConn) {
    $proc = Get-Process -Id $existingConn.OwningProcess -ErrorAction SilentlyContinue
    Write-Host "[WARNING] Port 8000 is already in use by PID $($existingConn.OwningProcess) ($($proc.ProcessName))." -ForegroundColor Yellow
    Write-Host "If this is a previous backend instance, you can terminate it with: Stop-Process -Id $($existingConn.OwningProcess) -Force`n" -ForegroundColor Yellow
}

# Set environment variables for local operation
$env:PYTHONPATH = "$ProjectRoot;$BackendDir"
$env:DATA_PATH = Join-Path $BackendDir "data\synthetic_students.json"
$env:INTERVENTIONS_PATH = Join-Path $BackendDir "data\interventions.json"
$env:TIMELINE_PATH = Join-Path $BackendDir "data\timeline_events.json"
$env:MODEL_DIR = Join-Path $ProjectRoot "ml\models"
$env:DATA_DIR = Join-Path $ProjectRoot "data"
$env:FRONTEND_ORIGIN = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:5173"

Set-Location $ProjectRoot

Write-Host "Launching uvicorn..." -ForegroundColor Green
Write-Host "  -> Backend API Base: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  -> Swagger Docs:    http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "  -> Health Endpoint: http://127.0.0.1:8000/health`n" -ForegroundColor Green

uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
