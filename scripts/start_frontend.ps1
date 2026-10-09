# scripts/start_frontend.ps1
# Starts the Student360 React/Vite Frontend Dev Server on Windows PowerShell

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Starting Student360 Frontend Development Server" -ForegroundColor Cyan
Write-Host "  Frontend Dir: $FrontendDir" -ForegroundColor DarkGray
Write-Host "=========================================================" -ForegroundColor Cyan

# Check if ports 3000 or 3001 are currently in use
foreach ($port in @(3000, 3001)) {
    $existing = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($existing) {
        $p = Get-Process -Id $existing.OwningProcess -ErrorAction SilentlyContinue
        Write-Host "[INFO] Port $port is in use by PID $($existing.OwningProcess) ($($p.ProcessName))." -ForegroundColor DarkYellow
    }
}

Set-Location $FrontendDir

Write-Host "`nStarting Vite development server..." -ForegroundColor Green
Write-Host "  -> Primary Frontend URL: http://localhost:3000 (or http://localhost:3001)" -ForegroundColor Green
Write-Host "  -> Login Page:           http://localhost:3000/login (or http://localhost:3001/login)`n" -ForegroundColor Green

npm run dev
