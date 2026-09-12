@echo off
title AI-CDSS Backend Server (FastAPI + CUDA)
cd /d "%~dp0backend"
echo ========================================================
echo   Starting AI-CDSS FastAPI Server on http://127.0.0.1:8000
echo   Swagger Documentation: http://127.0.0.1:8000/docs
echo ========================================================
env\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
