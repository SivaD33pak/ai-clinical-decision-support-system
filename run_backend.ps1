# AI-CDSS Backend Server Runner (PowerShell)
$backendDir = Join-Path $PSScriptRoot "backend"
Set-Location $backendDir
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting AI-CDSS FastAPI Server on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  Swagger Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
& ".\env\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
