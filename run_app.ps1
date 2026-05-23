# SMT Line 003 Production Intelligence Dashboard
# Streamlit App Launcher (PowerShell)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   STATIC//VOID - SMT Line 003 Production Intelligence" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Streamlit app..." -ForegroundColor Green
Write-Host "Dashboard will open at: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

streamlit run app.py

Read-Host "Press Enter to exit"
